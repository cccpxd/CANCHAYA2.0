from django.db import models


class Cancha(models.Model):
    class Tipo(models.TextChoices):
        FUTBOL = 'Futbol 5', 'Futbol 5'
        VOLEY = 'Volley playa', 'Volley playa'

    nombre = models.CharField(max_length=80)
    tipo = models.CharField(max_length=30, choices=Tipo.choices)
    precio_hora = models.DecimalField(max_digits=8, decimal_places=2)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def esta_disponible(self, fecha, hora_inicio, hora_fin, excluir_reserva_id=None):
        from django.db.models import Q
        ocupado = self.reservas.filter(
            fecha=fecha
        ).filter(Q(hora_inicio__lt=hora_fin) & Q(hora_fin__gt=hora_inicio))
        
        if excluir_reserva_id:
            ocupado = ocupado.exclude(pk=excluir_reserva_id)
            
        return not ocupado.exists()


class Reserva(models.Model):
    cancha = models.ForeignKey(Cancha, on_delete=models.CASCADE, related_name='reservas')
    nombre_cliente = models.CharField(max_length=100)
    telefono = models.CharField(max_length=30)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    creada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha', 'hora_inicio']

    def __str__(self):
        return f'{self.cancha} - {self.fecha} - {self.hora_inicio}'

class Torneos(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    canchas = models.ManyToManyField(Cancha, related_name='torneos')

    class Meta:
        ordering = ['fecha_inicio']

    def __str__(self):
        return self.nombre
