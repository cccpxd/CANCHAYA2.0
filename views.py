
from django.contrib import messages
from django.shortcuts import redirect, render

from .models import Cancha, Reserva
from .controllers.permisos import administrador_requerido


def inicio(request):
    canchas = Cancha.objects.all()
    perfil = getattr(request.user, 'perfil', None)
    es_administrador = bool(
        request.user.is_authenticated
        and request.user.is_superuser
        and perfil
        and perfil.es_administrador
    )

    return render(
        request,
        'inicio.html',
        {
            'canchas': canchas,
            'cantidad_activas': Cancha.objects.filter(activa=True).count(),
            'cantidad_reservas': Reserva.objects.count(),
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
