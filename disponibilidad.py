
"""Consulta de disponibilidad de una cancha.

La decisión de si un horario está libre la toma esta_disponible()
(logic.py). Este módulo consulta los datos mediante Django ORM,
valida la consulta, identifica los choques y calcula el total estimado.
También genera las franjas fijas del calendario (Fase 1).
"""

from datetime import date, datetime, time, timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.utils import timezone

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
    ).exclude(estado=Reserva.Estado.CANCELADA)

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


# ---------------------------------------------------------------------------
# Calendario de franjas (Fase 1)
# ---------------------------------------------------------------------------

def _configuracion_franjas():
    apertura = time.fromisoformat(settings.HORARIO_APERTURA)
    cierre = time.fromisoformat(settings.HORARIO_CIERRE)
    paso = timedelta(minutes=settings.DURACION_FRANJA_MINUTOS)
    return apertura, cierre, paso


def generar_franjas():
    """Devuelve los pares (inicio, fin) de un día, sin consultar la base."""
    apertura, cierre, paso = _configuracion_franjas()

    base = date(2000, 1, 1)
    cursor = datetime.combine(base, apertura)
    limite = datetime.combine(base, cierre)

    while cursor + paso <= limite:
        yield cursor.time(), (cursor + paso).time()
        cursor += paso


def semana_de(fecha):
    """Lunes de la semana a la que pertenece `fecha`."""
    return fecha - timedelta(days=fecha.weekday())


def _reservas_activas(cancha_id, desde, hasta):
    return Reserva.objects.filter(
        cancha_id=cancha_id,
        fecha__range=(desde, hasta),
    ).exclude(estado=Reserva.Estado.CANCELADA)


def franjas_del_dia(cancha, fecha, reservas=None):
    """Lista de franjas de una cancha en una fecha.

    Cada franja indica `inicio`, `fin`, `estado` ('libre', 'ocupado' o
    'pasado') y `precio`.
    """
    if reservas is None:
        reservas = list(_reservas_activas(cancha.id, fecha, fecha))

    hoy = timezone.localdate()
    ahora = timezone.localtime().time()

    franjas = []

    for inicio, fin in generar_franjas():
        if fecha < hoy or (fecha == hoy and inicio <= ahora):
            estado = 'pasado'
        elif any(
            reserva.hora_inicio < fin and reserva.hora_fin > inicio
            for reserva in reservas
        ):
            estado = 'ocupado'
        else:
            estado = 'libre'

        franjas.append({
            'inicio': inicio,
            'fin': fin,
            'estado': estado,
            'precio': _calcular_total(cancha.precio_hora, inicio, fin),
        })

    return franjas


def franjas_de_la_semana(cancha, lunes):
    """Siete días desde `lunes`, cada uno con sus franjas."""
    dias = [lunes + timedelta(days=indice) for indice in range(settings.DIAS_CALENDARIO)]

    reservas = list(_reservas_activas(cancha.id, dias[0], dias[-1]))

    return [
        {
            'fecha': dia,
            'franjas': franjas_del_dia(
                cancha,
                dia,
                [reserva for reserva in reservas if reserva.fecha == dia],
            ),
        }
        for dia in dias
    ]


def filas_de_semana(dias):
    """Transpone la semana a filas por hora, listas para pintar una tabla.

    Cada fila trae `inicio`, `fin` y una celda por día con su fecha y su
    franja, que es lo que necesitan tanto el calendario como el tablero de
    la portada.
    """
    return [
        {
            'inicio': inicio,
            'fin': fin,
            'celdas': [
                {'dia': dia['fecha'], 'franja': dia['franjas'][indice]}
                for dia in dias
            ],
        }
        for indice, (inicio, fin) in enumerate(generar_franjas())
    ]


def proximas_franjas_libres(cancha, cantidad=4):
    """Primeras franjas libres desde hoy, para el panel del inicio."""
    hoy = timezone.localdate()
    encontradas = []

    for desplazamiento in range(settings.DIAS_CALENDARIO + 1):
        dia = hoy + timedelta(days=desplazamiento)

        for franja in franjas_del_dia(cancha, dia):
            if franja['estado'] != 'libre':
                continue

            encontradas.append({
                'fecha': dia,
                **franja,
            })

            if len(encontradas) >= cantidad:
                return encontradas

    return encontradas
