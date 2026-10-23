from django.contrib import messages
from django.shortcuts import redirect, render

from .disponibilidad import CanchaNoEncontrada, consultar_disponibilidad
from .forms import CanchaForm, DisponibilidadForm, ReservaForm
from .logic import esta_disponible
from .models import Cancha, Reserva, canchas_activas


def inicio(request):
    canchas = [
        {**cancha, 'activa': cancha.get('activa', True)}
        for cancha in request.session.get('canchas', [])
    ]
    return render(
        request,
        'inicio.html',
        {
            'canchas': canchas,
            'cantidad_activas': len(canchas_activas(canchas)),
            'cantidad_reservas': len(request.session.get('reservas', [])),
        },
    )


def crear_cancha(request):
    if request.method == 'POST':
        form = CanchaForm(request.POST)
        if form.is_valid():
            canchas = request.session.get('canchas', [])
            cancha = Cancha(
                id=max((item['id'] for item in canchas), default=0) + 1,
                nombre=form.cleaned_data['nombre'],
                tipo=form.cleaned_data['tipo'],
                precio_hora=str(form.cleaned_data['precio_hora']),
                activa=form.cleaned_data['activa'],
            )
            canchas.append(cancha.__dict__)
            request.session['canchas'] = canchas
            return redirect('inicio')
    else:
        form = CanchaForm()
    return render(request, 'cancha_form.html', {'form': form})


def alternar_cancha(request, cancha_id):
    if request.method == 'POST':
        canchas = request.session.get('canchas', [])
        for cancha in canchas:
            if cancha['id'] == cancha_id:
                cancha['activa'] = not cancha.get('activa', True)
                estado = 'activada' if cancha['activa'] else 'desactivada'
                messages.success(
                    request, f"Cancha {estado}: {cancha['nombre']}."
                )
        request.session['canchas'] = canchas
    return redirect('inicio')


def crear_reserva(request):
    activas = canchas_activas(request.session.get('canchas', []))
    if request.method == 'POST':
        form = ReservaForm(request.POST, canchas=activas)
        if form.is_valid():
            datos = form.cleaned_data
            cancha_id = int(datos['cancha_id'])
            reservas = request.session.get('reservas', [])
            if esta_disponible(
                reservas,
                cancha_id,
                datos['fecha'],
                datos['hora_inicio'],
                datos['hora_fin'],
            ):
                cancha = next(item for item in activas if item['id'] == cancha_id)
                reserva = Reserva(
                    cancha_id=cancha_id,
                    cancha_nombre=cancha['nombre'],
                    nombre_cliente=datos['nombre_cliente'],
                    telefono=datos['telefono'],
                    fecha=datos['fecha'].isoformat(),
                    hora_inicio=datos['hora_inicio'].isoformat(timespec='minutes'),
                    hora_fin=datos['hora_fin'].isoformat(timespec='minutes'),
                )
                reservas.append(reserva.__dict__)
                request.session['reservas'] = reservas
                messages.success(request, 'Reserva creada correctamente.')
                return redirect('lista_reservas')
            form.add_error(None, 'Ese horario ya está ocupado para esta cancha.')
    else:
        form = ReservaForm(canchas=activas)
    return render(
        request,
        'reserva_form.html',
        {'form': form, 'tiene_canchas': bool(activas)},
    )


def lista_reservas(request):
    return render(
        request,
        'lista.html',
        {'reservas': request.session.get('reservas', [])},
    )


def disponibilidad(request):
    canchas = request.session.get('canchas', [])
    activas = canchas_activas(canchas)
    resultado = None
    error = None

    if request.GET:
        form = DisponibilidadForm(request.GET, canchas=activas)
        if form.is_valid():
            datos = form.cleaned_data
            try:
                resultado = consultar_disponibilidad(
                    canchas,
                    request.session.get('reservas', []),
                    int(datos['cancha_id']),
                    datos['fecha'],
                    datos['hora_inicio'],
                    datos['hora_fin'],
                )
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
            'tiene_canchas': bool(activas),
        },
    )


def reiniciar_datos(request):
    if request.method == 'POST':
        request.session.pop('canchas', None)
        request.session.pop('reservas', None)
    return redirect('inicio')
