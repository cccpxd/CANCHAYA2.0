from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import CanchaForm
from ..models import Cancha
from .permisos import administrador_requerido


@administrador_requerido
def crear_cancha(request):
	if request.method == 'POST':
		form = CanchaForm(request.POST)

		if form.is_valid():
			form.save()

			messages.success(request, 'Cancha creada correctamente.')
			return redirect('inicio')

	else:
		form = CanchaForm()

	return render(request, 'cancha_form.html', {'form': form})


@administrador_requerido
def alternar_cancha(request, cancha_id):
	if request.method == 'POST':
		cancha = get_object_or_404(Cancha, id=cancha_id)

		cancha.activa = not cancha.activa
		cancha.save()

		estado = 'activada' if cancha.activa else 'desactivada'

		messages.success(
			request,
			f'Cancha {estado}: {cancha.nombre}.'
		)

	return redirect('inicio')
