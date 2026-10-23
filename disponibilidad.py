"""Consulta de disponibilidad de una cancha.

La decisión de si un horario está libre la toma siempre esta_disponible()
(logic.py). Este módulo solo valida la consulta, identifica los choques y
calcula el total estimado.
"""

from datetime import date, time
from decimal import ROUND_HALF_UP, Decimal

from .logic import esta_disponible


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


def _buscar_cancha_activa(canchas, cancha_id):
    for cancha in canchas:
        if int(cancha['id']) == int(cancha_id) and cancha.get('activa', True):
            return cancha
    raise CanchaNoEncontrada('La cancha no existe o está inactiva.')


def _calcular_total(precio_hora, hora_inicio, hora_fin):
    minutos = (hora_fin.hour * 60 + hora_fin.minute) - (
        hora_inicio.hour * 60 + hora_inicio.minute
    )
    total = Decimal(str(precio_hora)) * Decimal(minutos) / Decimal(60)
    return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def consultar_disponibilidad(
    canchas, reservas, cancha_id, fecha, hora_inicio, hora_fin
):
    """Consulta si una cancha está libre en un intervalo horario.

    Devuelve {'disponible': bool, 'choques': list[dict], 'total': Decimal | None}.
    Lanza ValueError si los datos son inválidos y CanchaNoEncontrada si la
    cancha no existe o está inactiva.
    """
    _validar_consulta(fecha, hora_inicio, hora_fin)
    cancha = _buscar_cancha_activa(canchas, cancha_id)

    disponible = esta_disponible(
        reservas, cancha['id'], fecha, hora_inicio, hora_fin
    )
    if disponible:
        choques = []
        total = _calcular_total(cancha['precio_hora'], hora_inicio, hora_fin)
    else:
        choques = [
            reserva
            for reserva in reservas
            if not esta_disponible(
                [reserva], cancha['id'], fecha, hora_inicio, hora_fin
            )
        ]
        total = None

    return {'disponible': disponible, 'choques': choques, 'total': total}
