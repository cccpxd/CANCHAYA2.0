from django.test import TestCase
from datetime import date, time
from .models import Cancha, Reserva
from .forms import ReservaForm

class ReservaReglaTestCase(TestCase):
    def setUp(self):
        # Preparar los datos de prueba
        self.cancha = Cancha.objects.create(
            nombre="Cancha 1", tipo="Futbol 5", precio_hora=50000, activa=True
        )
        self.fecha_prueba = date(2026, 11, 20)

    # Prueba 1: Funcionalidad normal
    def test_crear_reserva_valida(self):
        form_data = {
            'cancha': self.cancha.id,
            'nombre_cliente': 'Juan Perez',
            'telefono': '3001234567',
            'fecha': self.fecha_prueba,
            'hora_inicio': time(14, 0),
            'hora_fin': time(15, 0)
        }
        form = ReservaForm(data=form_data)
        self.assertTrue(form.is_valid())

    # Prueba 2: Caso límite / Dato inválido (Hora fin menor a hora inicio)
    def test_reserva_invalida_hora_retrograda(self):
        form_data = {
            'cancha': self.cancha.id,
            'nombre_cliente': 'Juan Perez',
            'telefono': '3001234567',
            'fecha': self.fecha_prueba,
            'hora_inicio': time(16, 0),
            'hora_fin': time(15, 0) # Error intencional
        }
        form = ReservaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('hora_fin', form.errors)

    # Prueba 3: Regla de negocio (Solapamiento de horarios)
    def test_reserva_solapada(self):
        # Creamos una reserva previa
        Reserva.objects.create(
            cancha=self.cancha, nombre_cliente="Pedro", telefono="123",
            fecha=self.fecha_prueba, hora_inicio=time(14, 0), hora_fin=time(16, 0)
        )
        # Intentamos reservar en el mismo horario
        form_data = {
            'cancha': self.cancha.id,
            'nombre_cliente': 'Ana Lopez',
            'telefono': '3009876543',
            'fecha': self.fecha_prueba,
            'hora_inicio': time(15, 0),
            'hora_fin': time(17, 0)
        }
        form = ReservaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors) # Error de validación general