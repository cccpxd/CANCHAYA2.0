from datetime import date, time
from decimal import Decimal

from django.test import SimpleTestCase

from parcial.disponibilidad import CanchaNoEncontrada, consultar_disponibilidad
from parcial.logic import esta_disponible


class DisponibilidadReservaTests(SimpleTestCase):
    def setUp(self):
        self.fecha = date(2026, 11, 20)
        self.reservas = []

    def test_horario_libre_esta_disponible(self):
        self.assertTrue(
            esta_disponible(
                self.reservas, 1, self.fecha, time(14, 0), time(15, 0)
            )
        )

    def test_horario_solapado_no_esta_disponible(self):
        self.reservas.append(
            {
                'cancha_id': 1,
                'fecha': self.fecha,
                'hora_inicio': time(14, 0),
                'hora_fin': time(16, 0),
            }
        )

        self.assertFalse(
            esta_disponible(
                self.reservas, 1, self.fecha, time(15, 0), time(17, 0)
            )
        )

    def test_reserva_en_otra_cancha_no_bloquea(self):
        self.reservas.append(
            {
                'cancha_id': 2,
                'fecha': self.fecha,
                'hora_inicio': time(14, 0),
                'hora_fin': time(16, 0),
            }
        )

        self.assertTrue(
            esta_disponible(
                self.reservas, 1, self.fecha, time(15, 0), time(17, 0)
            )
        )

    def test_horarios_consecutivos_no_se_solapan(self):
        self.reservas.append(
            {
                'cancha_id': 1,
                'fecha': self.fecha,
                'hora_inicio': time(14, 0),
                'hora_fin': time(15, 0),
            }
        )

        self.assertTrue(
            esta_disponible(
                self.reservas, 1, self.fecha, time(15, 0), time(16, 0)
            )
        )

    def test_intervalo_invalido_no_esta_disponible(self):
        self.assertFalse(
            esta_disponible(
                self.reservas, 1, self.fecha, time(16, 0), time(15, 0)
            )
        )


class ConsultarDisponibilidadTests(SimpleTestCase):
    def setUp(self):
        self.fecha = date(2026, 11, 20)
        self.canchas = [
            {'id': 1, 'nombre': 'Cancha A', 'precio_hora': '50000.00'},
            {'id': 2, 'nombre': 'Cancha B', 'precio_hora': '60000.00',
             'activa': False},
        ]
        self.reservas = []

    def consultar(self, cancha_id=1, inicio=time(10, 0), fin=time(11, 0)):
        return consultar_disponibilidad(
            self.canchas, self.reservas, cancha_id, self.fecha, inicio, fin
        )

    def test_horario_disponible_devuelve_total(self):
        resultado = self.consultar(fin=time(12, 0))

        self.assertTrue(resultado['disponible'])
        self.assertEqual(resultado['total'], Decimal('100000.00'))

    def test_horario_ocupado_devuelve_choque(self):
        reserva = {
            'cancha_id': 1,
            'fecha': self.fecha.isoformat(),
            'hora_inicio': '10:00',
            'hora_fin': '11:00',
        }
        self.reservas.append(reserva)

        resultado = self.consultar(inicio=time(10, 30), fin=time(11, 30))

        self.assertFalse(resultado['disponible'])
        self.assertEqual(resultado['choques'], [reserva])
        self.assertIsNone(resultado['total'])

    def test_cancha_inactiva_no_se_puede_consultar(self):
        with self.assertRaises(CanchaNoEncontrada):
            self.consultar(cancha_id=2)
