
"""Consulta de disponibilidad de una cancha.

La decisión de si un horario está libre la toma esta_disponible()
(logic.py). Este módulo consulta los datos mediante Django ORM,
valida la consulta, identifica los choques y calcula el total estimado.
"""

from datetime import date, time
from decimal import ROUND_HALF_UP, Decimal

from .logic import esta_disponible
from .models import Cancha, Reserva


class CanchaNoEncontrada(Exception):
    """La cancha no existe o está inactiva."""


def _validar_consulta(fecha, hora_inicio, hora_fin):
    if not isinstance(fecha, date):
        raise ValueError('fecha debe ser date.')

    if not isinstance(hora_inicio, time):
        raise ValueError('hora_inicio debe ser time.')

    if not isinstance(hora_fin, time):
        raise ValueError('hora_fin debe ser time.')

    if hora_inicio >= hora_fin:
        raise ValueError('hora_inicio debe ser menor que hora_fin.')


def _buscar_cancha_activa(cancha_id):
    try:
        return Cancha.objects.get(
            id=cancha_id,
            activa=True
        )
    except Cancha.DoesNotExist:
        raise CanchaNoEncontrada(
            'La cancha no existe o está inactiva.'
        ) from None


def _calcular_total(precio_hora, hora_inicio, hora_fin):
    minutos = (
        hora_fin.hour * 60 + hora_fin.minute
    ) - (
        hora_inicio.hour * 60 + hora_inicio.minute
    )

    total = (
        Decimal(str(precio_hora)) * Decimal(minutos) / Decimal(60)
    )

    return total.quantize(
        Decimal('0.01'),
        rounding=ROUND_HALF_UP
    )



def consultar_disponibilidad(
    cancha_id,
    fecha,
    hora_inicio,
    hora_fin
):
    """Consulta si una cancha está libre en un intervalo horario."""

    # 1. Validar los datos recibidos.
    _validar_consulta(fecha, hora_inicio, hora_fin)

    # 2. Buscar la cancha en la base de datos.
    cancha = _buscar_cancha_activa(cancha_id)

    # 3. Consultar las reservas de esa cancha para esa fecha.
    reservas = Reserva.objects.filter(
        cancha=cancha,
        fecha=fecha
    )

    # 4. Comprobar si el horario está disponible.
    disponible = esta_disponible(
        reservas,
        cancha.id,
        fecha,
        hora_inicio,
        hora_fin
    )

    # 5. Calcular el resultado.
    if disponible:
        choques = []

        total = _calcular_total(
            cancha.precio_hora,
            hora_inicio,
            hora_fin
        )

    else:
        choques = reservas.filter(
            hora_inicio__lt=hora_fin,
            hora_fin__gt=hora_inicio
        )

        total = None

    # 6. Devolver los resultados.
    return {
        'disponible': disponible,
        'choques': choques,
        'total': total
    }
