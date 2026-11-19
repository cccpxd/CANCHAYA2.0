from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ..disponibilidad import CanchaNoEncontrada, consultar_disponibilidad
from ..forms import DisponibilidadForm, ReservaForm
from ..models import Cancha, Reserva


@login_required
def crear_reserva(request):
	activas = Cancha.objects.filter(activa=True)

	if request.method == 'POST':
		form = ReservaForm(request.POST, canchas=activas)

		if form.is_valid():
			datos = form.cleaned_data

			cancha = get_object_or_404(
				Cancha,
				id=datos['cancha_id'],
				activa=True
			)

			if consultar_disponibilidad(
				cancha.id,
				datos['fecha'],
				datos['hora_inicio'],
				datos['hora_fin'],
			)['disponible']:

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

				reserva.save()

				messages.success(
					request,
					'Reserva creada correctamente.'
				)

				return redirect('lista_reservas')

			form.add_error(
				None,
				'Ese horario ya está ocupado para esta cancha.'
			)

	else:
		form = ReservaForm(canchas=activas)

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
	reservas = Reserva.objects.select_related('cancha', 'usuario').all()
	perfil = getattr(request.user, 'perfil', None)
	if not (perfil and perfil.es_administrador):
		reservas = reservas.filter(usuario=request.user)

	return render(
		request,
		'lista.html',
		{
			'reservas': reservas,
		},
	)


def disponibilidad(request):
	activas = Cancha.objects.filter(activa=True)

	resultado = None
	error = None

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
			'tiene_canchas': activas.exists(),
		},
	)
