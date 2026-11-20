from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Usuario(models.Model):

    class Rol(models.TextChoices):
        CLIENTE = 'CLIENTE', 'Cliente'
        ADMINISTRADOR = 'ADMINISTRADOR', 'Administrador'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil',
    )
    telefono = models.CharField(max_length=30, blank=True)
    rol = models.CharField(
        max_length=16,
        choices=Rol.choices,
        default=Rol.CLIENTE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['rol'],
                condition=Q(rol='ADMINISTRADOR'),
                name='un_solo_usuario_administrador',
            ),
        ]

    @property
    def es_administrador(self):
        return self.rol == self.Rol.ADMINISTRADOR

    def __str__(self):
        return self.user.get_username()


class Cancha(models.Model):

    TIPOS_CANCHA = [
        ('Futbol 5', 'Fútbol 5'),
        ('Volley playa', 'Vóley playa'),
    ]

    nombre = models.CharField(max_length=80)

    tipo = models.CharField(
        max_length=30,
        choices=TIPOS_CANCHA
    )

    precio_hora = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Reserva(models.Model):

    class Estado(models.TextChoices):
        CONFIRMADA = 'CONFIRMADA', 'Confirmada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='reservas',
        null=True,
        blank=True,
    )

    cancha = models.ForeignKey(
        Cancha,
        on_delete=models.PROTECT,
        related_name='reservas'
    )

    nombre_cliente = models.CharField(max_length=100)

    telefono = models.CharField(max_length=30)

    fecha = models.DateField()

    hora_inicio = models.TimeField()

    hora_fin = models.TimeField()

    estado = models.CharField(
        max_length=12,
        choices=Estado.choices,
        default=Estado.CONFIRMADA,
    )

    creada = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        ordering = ['fecha', 'hora_inicio']

    @property
    def activa(self):
        return self.estado != self.Estado.CANCELADA

    @property
    def puede_cancelarse(self):
        if not self.activa:
            return False

        ahora = timezone.localtime().replace(tzinfo=None)
        return datetime.combine(self.fecha, self.hora_inicio) > ahora

    def clean(self):
        super().clean()
        errores = {}

        if self.hora_inicio and self.hora_fin and self.hora_inicio >= self.hora_fin:
            errores['hora_fin'] = (
                'La hora final debe ser posterior a la hora inicial.'
            )

        if self.fecha and self.fecha < timezone.localdate():
            errores['fecha'] = 'La fecha no puede estar en el pasado.'

        if (
            self.activa
            and self.cancha_id
            and self.fecha
            and self.hora_inicio
            and self.hora_fin
        ):
            choques = Reserva.objects.filter(
                cancha_id=self.cancha_id,
                fecha=self.fecha,
                hora_inicio__lt=self.hora_fin,
                hora_fin__gt=self.hora_inicio,
            ).exclude(estado=self.Estado.CANCELADA)

            if self.pk:
                choques = choques.exclude(pk=self.pk)

            if choques.exists():
                errores['__all__'] = (
                    'Ese horario ya está ocupado para esta cancha.'
                )

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        # Valida también cuando se crea desde el admin o desde el shell.
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Reserva {self.id} - {self.cancha.nombre}"
