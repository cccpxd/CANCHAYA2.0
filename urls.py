from django.urls import path

from . import views
from .controllers import canchas_controller, reservas_controller, usuarios_controller


urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('calendario/', reservas_controller.calendario, name='calendario'),
    path('api/disponibilidad/', reservas_controller.api_disponibilidad, name='api_disponibilidad'),
    path('canchas/nueva/', canchas_controller.crear_cancha, name='crear_cancha'),
    path('canchas/<int:cancha_id>/alternar/', canchas_controller.alternar_cancha, name='alternar_cancha'),
    path('reservar/', reservas_controller.crear_reserva, name='crear_reserva'),
    path('reservas/', reservas_controller.lista_reservas, name='lista_reservas'),
    path('reservas/<int:reserva_id>/cancelar/', reservas_controller.cancelar_reserva, name='cancelar_reserva'),
    path('disponibilidad/', reservas_controller.disponibilidad, name='disponibilidad'),
    path('reiniciar/', views.reiniciar_datos, name='reiniciar_datos'),
    path('registro/', usuarios_controller.registro, name='registro'),
    path('iniciar-sesion/', usuarios_controller.iniciar_sesion, name='iniciar_sesion'),
    path('cerrar-sesion/', usuarios_controller.cerrar_sesion, name='cerrar_sesion'),
]
