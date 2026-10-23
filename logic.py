from datetime import date, time


def _convertir_fecha(valor: date | str) -> date:
    return valor if isinstance(valor, date) else date.fromisoformat(valor)


def _convertir_hora(valor: time | str) -> time:
    return valor if isinstance(valor, time) else time.fromisoformat(valor)


def _reserva_se_solapa(
    reserva: dict,
    cancha_id: int,
    fecha: date,
    hora_inicio: time,
    hora_fin: time,
) -> bool:
    try:
        misma_cancha = int(reserva['cancha_id']) == int(cancha_id)
        misma_fecha = _convertir_fecha(reserva['fecha']) == fecha
        inicio_existente = _convertir_hora(reserva['hora_inicio'])
        fin_existente = _convertir_hora(reserva['hora_fin'])
    except (KeyError, TypeError, ValueError):
        return False

    return (
        misma_cancha
        and misma_fecha
        and inicio_existente < hora_fin
        and fin_existente > hora_inicio
    )

def fecha_valida(fecha: date | str) -> bool:
    fecha_convertida = _convertir_fecha(fecha)
    return fecha_convertida >= date.today()


def esta_disponible(
    reservas: list[dict],
    cancha_id: int,
    fecha: date | str,
    hora_inicio: time | str,
    hora_fin: time | str,
) -> bool:
    if not fecha_valida(fecha):
        return False

    fecha_solicitada = _convertir_fecha(fecha)
    inicio_solicitado = _convertir_hora(hora_inicio)
    fin_solicitado = _convertir_hora(hora_fin)

    if inicio_solicitado >= fin_solicitado:
        return False

    return not any(
        _reserva_se_solapa(
            reserva,
            cancha_id,
            fecha_solicitada,
            inicio_solicitado,
            fin_solicitado,
        )
        for reserva in reservas
    )