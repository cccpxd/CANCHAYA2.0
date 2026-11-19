from django.conf import settings
from django.db import models
from django.db.models import Q


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

    def __str__(self):
        return self.nombre


class Reserva(models.Model):

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

    def __str__(self):
        return f"Reserva {self.id} - {self.cancha.nombre}"