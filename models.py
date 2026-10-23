from dataclasses import dataclass


@dataclass(frozen=True)
class Cancha:
    id: int
    nombre: str
    tipo: str
    precio_hora: str
    activa: bool = True


@dataclass(frozen=True)
class Reserva:
    cancha_id: int
    cancha_nombre: str
    nombre_cliente: str
    telefono: str
    fecha: str
    hora_inicio: str
    hora_fin: str


def canchas_activas(canchas):
    """Devuelve solo las canchas activas (sin el campo 'activa' se asumen activas)."""
    return [cancha for cancha in canchas if cancha.get('activa', True)]
