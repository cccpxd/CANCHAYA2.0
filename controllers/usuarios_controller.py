from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from ..forms import RegistroForm


def _destino_seguro(request):
    destino = request.POST.get('next') or request.GET.get('next')
    if destino and url_has_allowed_host_and_scheme(
        destino,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return destino
    return reverse('inicio')


def registro(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, 'Tu cuenta fue creada correctamente.')
            return redirect(_destino_seguro(request))
    else:
        form = RegistroForm()

    return render(
        request,
        'registro.html',
        {'form': form, 'next': request.GET.get('next', '')},
    )


def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    form = AuthenticationForm(request, data=request.POST or None)
    form.fields['username'].label = 'Nombre de usuario'
    form.fields['password'].label = 'Contraseña'
    if request.method == 'POST' and form.is_valid():
        usuario = form.get_user()
        login(request, usuario)
        messages.success(request, 'Iniciaste sesión correctamente.')
        return redirect(_destino_seguro(request))

    return render(
        request,
        'iniciar_sesion.html',
        {'form': form, 'next': request.GET.get('next', '')},
    )


def cerrar_sesion(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Cerraste sesión.')
    return redirect('inicio')