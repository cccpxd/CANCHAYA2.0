from datetime import timedelta

from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone

from .controllers.permisos import administrador_requerido
from .disponibilidad import (
    filas_de_semana,
    franjas_de_la_semana,
    generar_franjas,
    semana_de,
)
from .models import Cancha, Reserva


def inicio(request):
    canchas = Cancha.objects.all()
    perfil = getattr(request.user, 'perfil', None)
    es_administrador = bool(
        request.user.is_authenticated
        and request.user.is_superuser
        and perfil
        and perfil.es_administrador
    )

    destacada = canchas.filter(activa=True).first()
    hoy = timezone.localdate()
    lunes = semana_de(hoy)

    dias = franjas_de_la_semana(destacada, lunes) if destacada else []
    filas = filas_de_semana(dias) if dias else []
    domingo = lunes + timedelta(days=len(dias) - 1) if dias else lunes

    libres_hoy = sum(
        1
        for fila in filas
        for celda in fila['celdas']
        if celda['dia'] == hoy and celda['franja']['estado'] == 'libre'
    )
    libres_semana = sum(
        1
        for fila in filas
        for celda in fila['celdas']
        if celda['franja']['estado'] == 'libre'
    )

    return render(
        request,
        'inicio.html',
        {
            'canchas': canchas,
            'cantidad_activas': Cancha.objects.filter(activa=True).count(),
            'cantidad_reservas': Reserva.objects.exclude(
                estado=Reserva.Estado.CANCELADA
            ).count(),
            'reservas_hoy': Reserva.objects.filter(fecha=hoy)
            .exclude(estado=Reserva.Estado.CANCELADA)
            .count(),
            'destacada': destacada,
            'dias': dias,
            'filas': filas,
            'lunes': lunes,
            'domingo': domingo,
            'libres_hoy': libres_hoy,
            'libres_semana': libres_semana,
            'franjas_por_dia': sum(1 for _ in generar_franjas()),
            'hoy': hoy,
            'es_administrador': es_administrador,
        },
    )


@administrador_requerido
def reiniciar_datos(request):
    if request.method == 'POST':
        Reserva.objects.all().delete()
        Cancha.objects.all().delete()

        messages.success(
            request,
            'Los datos fueron reiniciados correctamente.'
        )

    return redirect('inicio')
