from datetime import time, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import Cancha, Reserva


CANCHAS = [
    ('La Bombonera', 'Futbol 5', '55000.00'),
    ('El Campín', 'Futbol 5', '62000.00'),
    ('Arena Playa', 'Volley playa', '48000.00'),
]

RESERVAS = [
    (0, 1, time(19, 0), time(20, 0)),
    (0, 1, time(20, 0), time(21, 0)),
    (1, 0, time(18, 0), time(19, 0)),
    (2, 2, time(17, 0), time(18, 0)),
]


class Command(BaseCommand):
    help = 'Carga canchas y reservas de ejemplo para probar la aplicación.'

    def handle(self, *args, **options):
        canchas = []

        for nombre, tipo, precio in CANCHAS:
            cancha, creada = Cancha.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'tipo': tipo,
                    'precio_hora': Decimal(precio),
                    'activa': True,
                },
            )
            canchas.append(cancha)
            if creada:
                self.stdout.write(f'Cancha creada: {nombre}')

        hoy = timezone.localdate()
        creadas = 0

        for dias, indice, inicio, fin in RESERVAS:
            cancha = canchas[indice]

            existe = Reserva.objects.filter(
                cancha=cancha,
                fecha=hoy + timedelta(days=dias),
                hora_inicio=inicio,
            ).exists()
            if existe:
                continue

            try:
                Reserva.objects.create(
                    cancha=cancha,
                    nombre_cliente='Cliente de ejemplo',
                    telefono='3001234567',
                    fecha=hoy + timedelta(days=dias),
                    hora_inicio=inicio,
                    hora_fin=fin,
                )
                creadas += 1
            except ValidationError:
                self.stdout.write(
                    self.style.WARNING(
                        f'Saltada reserva {cancha.nombre} {inicio}: horario ocupado.'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Datos de ejemplo listos: {len(canchas)} canchas, {creadas} reservas nuevas.'
            )
        )
