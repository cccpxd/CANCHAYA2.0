from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ..disponibilidad import (
    CanchaNoEncontrada,
    consultar_disponibilidad,
    filas_de_semana,
    franjas_de_la_semana,
    franjas_del_dia,
    semana_de,
)
from ..forms import DisponibilidadForm, ReservaForm
from ..models import Cancha, Reserva


def _inicial_desde_get(request):
    inicial = {}
    for campo in ('cancha_id', 'fecha', 'hora_inicio', 'hora_fin'):
        valor = request.GET.get(campo)
        if valor:
            inicial[campo] = valor
    return inicial


def _es_administrador(request):
    perfil = getattr(request.user, 'perfil', None)
    return bool(
        request.user.is_authenticated
        and request.user.is_superuser
        and perfil
        and perfil.es_administrador
    )


@login_required
def crear_reserva(request):
    activas = Cancha.objects.filter(activa=True)

    if request.method == 'POST':
        form = ReservaForm(request.POST, canchas=activas)

        if form.is_valid():
            datos = form.cleaned_data

            try:
                with transaction.atomic():
                    # Bloquea la cancha para que dos reservas simultáneas no
                    # entren al mismo horario (condición de carrera).
                    cancha = Cancha.objects.select_for_update().get(
                        id=datos['cancha_id'],
                        activa=True,
                    )

                    disponible = consultar_disponibilidad(
                        cancha.id,
                        datos['fecha'],
                        datos['hora_inicio'],
                        datos['hora_fin'],
                    )['disponible']

                    if not disponible:
                        form.add_error(
                            None,
                            'Ese horario ya está ocupado para esta cancha.'
                        )
                    else:
                        reserva = Reserva(
                            usuario=request.user,
                            cancha=cancha,
                            nombre_cliente=(
                                request.user.get_full_name()
                                or request.user.get_username()
                            ),
                            telefono=getattr(
                                getattr(request.user, 'perfil', None),
                                'telefono',
                                '',
                            ),
                            fecha=datos['fecha'],
                            hora_inicio=datos['hora_inicio'],
                            hora_fin=datos['hora_fin'],
                        )

                        try:
                            reserva.save()
                        except ValidationError as error:
                            form.add_error(None, error)
                        else:
                            messages.success(
                                request,
                                'Reserva creada correctamente.'
                            )
                            return redirect('lista_reservas')

            except Cancha.DoesNotExist:
                form.add_error(
                    'cancha_id',
                    'La cancha ya no está disponible.'
                )

    else:
        form = ReservaForm(
            canchas=activas,
            initial=_inicial_desde_get(request),
        )

    return render(
        request,
        'reserva_form.html',
        {
            'form': form,
            'tiene_canchas': activas.exists(),
        },
    )


@login_required
def lista_reservas(request):
    reservas = Reserva.objects.select_related('cancha', 'usuario').order_by(
        '-fecha', '-hora_inicio'
    )
    perfil = getattr(request.user, 'perfil', None)
    if not (perfil and perfil.es_administrador):
        reservas = reservas.filter(usuario=request.user)

    return render(
        request,
        'lista.html',
        {
            'reservas': reservas,
            'hoy': timezone.localdate(),
        },
    )


@login_required
def cancelar_reserva(request, reserva_id):
    if request.method != 'POST':
        return redirect('lista_reservas')

    reserva = get_object_or_404(Reserva, id=reserva_id)

    if reserva.usuario_id != request.user.id and not _es_administrador(request):
        messages.error(request, 'No puedes cancelar una reserva ajena.')
        return redirect('lista_reservas')

    if not reserva.puede_cancelarse:
        messages.error(request, 'Esta reserva ya no se puede cancelar.')
        return redirect('lista_reservas')

    reserva.estado = Reserva.Estado.CANCELADA
    reserva.save()

    messages.success(
        request,
        'Reserva cancelada. Ese horario volvió a quedar libre.'
    )
    return redirect('lista_reservas')


def disponibilidad(request):
    activas = Cancha.objects.filter(activa=True)

    resultado = None
    error = None
    franjas = []
    consulta = None

    if request.GET:
        form = DisponibilidadForm(request.GET, canchas=activas)

        if form.is_valid():
            datos = form.cleaned_data

            try:
                resultado = consultar_disponibilidad(
                    int(datos['cancha_id']),
                    datos['fecha'],
                    datos['hora_inicio'],
                    datos['hora_fin'],
                )
                franjas = franjas_del_dia(
                    Cancha.objects.get(id=datos['cancha_id']),
                    datos['fecha'],
                )
                consulta = {
                    'cancha_id': datos['cancha_id'],
                    'fecha': datos['fecha'].isoformat(),
                    'hora_inicio': datos['hora_inicio'].strftime('%H:%M'),
                    'hora_fin': datos['hora_fin'].strftime('%H:%M'),
                }

            except (ValueError, CanchaNoEncontrada) as problema:
                error = str(problema)

    else:
        form = DisponibilidadForm(canchas=activas)

    return render(
        request,
        'disponibilidad.html',
        {
            'form': form,
            'resultado': resultado,
            'error': error,
            'franjas': franjas,
            'consulta': consulta,
            'tiene_canchas': activas.exists(),
        },
    )


def calendario(request):
    canchas = Cancha.objects.filter(activa=True)

    cancha = None
    if canchas.exists():
        cancha_id = request.GET.get('cancha') or request.GET.get('cancha_id')
        if cancha_id and str(cancha_id).isdigit():
            cancha = canchas.filter(id=int(cancha_id)).first()
        if cancha is None:
            cancha = canchas.first()

    referencia = timezone.localdate()
    semana_param = request.GET.get('semana')
    if semana_param:
        try:
            referencia = date.fromisoformat(semana_param)
        except ValueError:
            referencia = timezone.localdate()

    lunes = semana_de(referencia)
    dias = franjas_de_la_semana(cancha, lunes) if cancha else []
    filas = filas_de_semana(dias)

    return render(
        request,
        'calendario.html',
        {
            'canchas': canchas,
            'cancha': cancha,
            'dias': dias,
            'filas': filas,
            'lunes': lunes,
            'domingo': lunes + timedelta(days=len(dias) - 1) if dias else lunes,
            'semana': lunes,
            'anterior': lunes - timedelta(days=7),
            'siguiente': lunes + timedelta(days=7),
            'hoy': timezone.localdate(),
            'tiene_canchas': canchas.exists(),
        },
    )


def api_disponibilidad(request):
    cancha_id = request.GET.get('cancha_id') or request.GET.get('cancha')

    if not cancha_id or not str(cancha_id).isdigit():
        return JsonResponse(
            {'error': 'cancha_id es obligatorio.'},
            status=400,
        )

    cancha = Cancha.objects.filter(id=int(cancha_id), activa=True).first()
    if cancha is None:
        return JsonResponse(
            {'error': 'La cancha no existe o está inactiva.'},
            status=404,
        )

    def serializar(franja):
        return {
            'inicio': franja['inicio'].strftime('%H:%M'),
            'fin': franja['fin'].strftime('%H:%M'),
            'estado': franja['estado'],
            'precio': str(franja['precio']),
        }

    semana_param = request.GET.get('semana')
    if semana_param:
        try:
            lunes = semana_de(date.fromisoformat(semana_param))
        except ValueError:
            return JsonResponse(
                {'error': 'semana debe tener formato YYYY-MM-DD.'},
                status=400,
            )

        dias = franjas_de_la_semana(cancha, lunes)

        return JsonResponse({
            'cancha': cancha.id,
            'dias': [
                {
                    'fecha': dia['fecha'].isoformat(),
                    'franjas': [serializar(f) for f in dia['franjas']],
                }
                for dia in dias
            ],
        })

    fecha_param = request.GET.get('fecha')
    try:
        fecha = date.fromisoformat(fecha_param) if fecha_param else timezone.localdate()
    except ValueError:
        return JsonResponse(
            {'error': 'fecha debe tener formato YYYY-MM-DD.'},
            status=400,
        )

    return JsonResponse({
        'cancha': cancha.id,
        'fecha': fecha.isoformat(),
        'franjas': [serializar(f) for f in franjas_del_dia(cancha, fecha)],
    })
