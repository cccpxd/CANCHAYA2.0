from django.contrib import admin

from .models import Cancha, Reserva


@admin.register(Cancha)
class CanchaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'precio_hora', 'activa')
    list_filter = ('tipo', 'activa')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('cancha', 'nombre_cliente', 'fecha', 'hora_inicio', 'hora_fin')
    list_filter = ('cancha', 'fecha')
