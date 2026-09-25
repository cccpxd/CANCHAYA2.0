from django.urls import path

from . import views

app_name = 'reservas'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('reservar/', views.crear_reserva, name='crear'),
    path('reservas/', views.lista_reservas, name='lista'),
]
