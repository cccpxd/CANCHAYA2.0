from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def administrador_requerido(view):
    @login_required
    @wraps(view)
    def comprobar_administrador(request, *args, **kwargs):
        perfil = getattr(request.user, 'perfil', None)
        if not (
            request.user.is_superuser
            and perfil
            and perfil.es_administrador
        ):
            messages.error(request, 'Esta acción es exclusiva del administrador.')
            return redirect('inicio')

        return view(request, *args, **kwargs)

    return comprobar_administrador