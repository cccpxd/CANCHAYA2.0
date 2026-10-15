from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render

from .forms import ReservaForm
from .models import Cancha, Reserva, Torneos


def inicio(request):
    canchas = Cancha.objects.filter(activa=True)
    return render(request, 'reservas/inicio.html', {'canchas': canchas})


@transaction.atomic
def crear_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reserva creada correctamente.')
            return redirect('reservas:lista')
    else:
        form = ReservaForm()
    return render(request, 'reservas/reserva_form.html', {'form': form})


def lista_reservas(request):
    reservas = Reserva.objects.select_related('cancha').all()
    return render(request, 'reservas/lista.html', {'reservas': reservas})

def lista_torneos(request):
    torneos = Torneos.objects.all()
    return render(request, 'reservas/torneos.html', {'torneos': torneos})

