from django.urls import path

from parcial import views


urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('canchas/nueva/', views.crear_cancha, name='crear_cancha'),
    path('canchas/<int:cancha_id>/alternar/', views.alternar_cancha, name='alternar_cancha'),
    path('reservar/', views.crear_reserva, name='crear_reserva'),
    path('reservas/', views.lista_reservas, name='lista_reservas'),
    path('disponibilidad/', views.disponibilidad, name='disponibilidad'),
    path('reiniciar/', views.reiniciar_datos, name='reiniciar_datos'),
]
