
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .disponibilidad import (
    CanchaNoEncontrada,
    consultar_disponibilidad,
    franjas_del_dia,
)
from .forms import ReservaForm
from .logic import esta_disponible
from .models import Cancha, Reserva, Usuario


class DisponibilidadReservaTests(TestCase):

    def setUp(self):
        # Utilizamos una fecha futura para que los tests no caduquen.
        self.fecha = date.today() + timedelta(days=7)

        self.cancha_a = Cancha.objects.create(
            nombre='Cancha A',
            tipo='Futbol 5',
            precio_hora=Decimal('50000.00'),
            activa=True,
        )

        self.cancha_b = Cancha.objects.create(
            nombre='Cancha B',
            tipo='Volley playa',
            precio_hora=Decimal('60000.00'),
            activa=False,
        )

    def crear_reserva(
        self,
        cancha=None,
        inicio=time(14, 0),
        fin=time(16, 0),
    ):
        return Reserva.objects.create(
            cancha=cancha or self.cancha_a,
            nombre_cliente='Cliente de prueba',
            telefono='3001234567',
            fecha=self.fecha,
            hora_inicio=inicio,
            hora_fin=fin,
        )

    # -----------------------------------------
    # Pruebas de logic.py
    # -----------------------------------------

    def test_horario_libre_esta_disponible(self):
        disponible = esta_disponible(
            Reserva.objects.filter(cancha=self.cancha_a),
            self.cancha_a.id,
            self.fecha,
            time(14, 0),
            time(15, 0),
        )

        self.assertTrue(disponible)

    def test_horario_solapado_no_esta_disponible(self):
        self.crear_reserva(
            inicio=time(14, 0),
            fin=time(16, 0),
        )

        disponible = esta_disponible(
            Reserva.objects.filter(cancha=self.cancha_a),
            self.cancha_a.id,
            self.fecha,
            time(15, 0),
            time(17, 0),
        )

        self.assertFalse(disponible)

    def test_reserva_en_otra_cancha_no_bloquea(self):
        self.crear_reserva(
            cancha=self.cancha_a,
            inicio=time(14, 0),
            fin=time(16, 0),
        )

        disponible = esta_disponible(
            Reserva.objects.filter(cancha=self.cancha_b),
            self.cancha_b.id,
            self.fecha,
            time(15, 0),
            time(17, 0),
        )

        self.assertTrue(disponible)

    def test_horarios_consecutivos_no_se_solapan(self):
        self.crear_reserva(
            inicio=time(14, 0),
            fin=time(15, 0),
        )

        disponible = esta_disponible(
            Reserva.objects.filter(cancha=self.cancha_a),
            self.cancha_a.id,
            self.fecha,
            time(15, 0),
            time(16, 0),
        )

        self.assertTrue(disponible)

    def test_intervalo_invalido_no_esta_disponible(self):
        disponible = esta_disponible(
            Reserva.objects.filter(cancha=self.cancha_a),
            self.cancha_a.id,
            self.fecha,
            time(16, 0),
            time(15, 0),
        )

        self.assertFalse(disponible)

    def test_fecha_pasada_no_esta_disponible(self):
        disponible = esta_disponible(
            Reserva.objects.filter(cancha=self.cancha_a),
            self.cancha_a.id,
            date.today() - timedelta(days=1),
            time(14, 0),
            time(15, 0),
        )

        self.assertFalse(disponible)

    # -----------------------------------------
    # Pruebas de disponibilidad.py
    # -----------------------------------------

    def test_horario_disponible_devuelve_total(self):
        resultado = consultar_disponibilidad(
            self.cancha_a.id,
            self.fecha,
            time(10, 0),
            time(12, 0),
        )

        self.assertTrue(resultado['disponible'])
        self.assertEqual(resultado['choques'], [])
        self.assertEqual(
            resultado['total'],
            Decimal('100000.00'),
        )

    def test_horario_ocupado_devuelve_choque(self):
        reserva = self.crear_reserva(
            inicio=time(10, 0),
            fin=time(11, 0),
        )

        resultado = consultar_disponibilidad(
            self.cancha_a.id,
            self.fecha,
            time(10, 30),
            time(11, 30),
        )

        self.assertFalse(resultado['disponible'])
        self.assertEqual(
            list(resultado['choques']),
            [reserva],
        )
        self.assertIsNone(resultado['total'])

    def test_cancha_inactiva_no_se_puede_consultar(self):
        with self.assertRaises(CanchaNoEncontrada):
            consultar_disponibilidad(
                self.cancha_b.id,
                self.fecha,
                time(10, 0),
                time(11, 0),
            )

    def test_cancha_inexistente_no_se_puede_consultar(self):
        with self.assertRaises(CanchaNoEncontrada):
            consultar_disponibilidad(
                99999,
                self.fecha,
                time(10, 0),
                time(11, 0),
            )

    def test_intervalo_invalido_lanza_error(self):
        with self.assertRaises(ValueError):
            consultar_disponibilidad(
                self.cancha_a.id,
                self.fecha,
                time(16, 0),
                time(15, 0),
            )


class AutenticacionYPermisosTests(TestCase):

    def setUp(self):
        self.fecha = date.today() + timedelta(days=7)
        self.cancha = Cancha.objects.create(
            nombre='Cancha de prueba',
            tipo='Futbol 5',
            precio_hora=Decimal('50000.00'),
        )

    def registrar_cliente(self):
        return self.client.post(
            reverse('registro'),
            {
                'first_name': 'Ana',
                'last_name': 'Prueba',
                'username': 'ana_prueba',
                'email': 'ana@example.com',
                'telefono': '3001234567',
                'password1': 'CanchaSegura2026!',
                'password2': 'CanchaSegura2026!',
            },
        )

    def test_usuario_sin_sesion_es_enviado_a_iniciar_sesion(self):
        respuesta = self.client.get(reverse('crear_reserva'))

        self.assertRedirects(
            respuesta,
            '/iniciar-sesion/?next=/reservar/',
        )

    def test_registro_crea_perfil_de_cliente_y_inicia_sesion(self):
        respuesta = self.registrar_cliente()
        usuario = get_user_model().objects.get(username='ana_prueba')

        self.assertRedirects(respuesta, reverse('inicio'))
        self.assertTrue(respuesta.wsgi_request.user.is_authenticated)
        self.assertEqual(usuario.perfil.rol, Usuario.Rol.CLIENTE)
        self.assertEqual(usuario.perfil.telefono, '3001234567')

    def test_cliente_registrado_puede_reservar(self):
        self.registrar_cliente()

        respuesta = self.client.post(
            reverse('crear_reserva'),
            {
                'cancha_id': str(self.cancha.id),
                'fecha': self.fecha.isoformat(),
                'hora_inicio': '14:00',
                'hora_fin': '15:00',
            },
        )

        reserva = Reserva.objects.get()
        self.assertRedirects(respuesta, reverse('lista_reservas'))
        self.assertEqual(reserva.usuario.username, 'ana_prueba')
        self.assertEqual(reserva.nombre_cliente, 'Ana Prueba')

    def test_cliente_no_puede_crear_canchas(self):
        self.registrar_cliente()

        respuesta = self.client.post(
            reverse('crear_cancha'),
            {
                'nombre': 'Cancha no autorizada',
                'tipo': 'Futbol 5',
                'precio_hora': '50000.00',
                'activa': 'on',
            },
        )

        self.assertRedirects(respuesta, reverse('inicio'))
        self.assertFalse(Cancha.objects.filter(nombre='Cancha no autorizada').exists())

    def test_solo_puede_existir_un_perfil_administrador(self):
        user_model = get_user_model()
        primer_usuario = user_model.objects.create_superuser(
            username='admin_uno',
            email='admin1@example.com',
            password='CanchaSegura2026!',
        )
        segundo_usuario = user_model.objects.create_superuser(
            username='admin_dos',
            email='admin2@example.com',
            password='CanchaSegura2026!',
        )
        Usuario.objects.create(
            user=primer_usuario,
            rol=Usuario.Rol.ADMINISTRADOR,
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            Usuario.objects.create(
                user=segundo_usuario,
                rol=Usuario.Rol.ADMINISTRADOR,
            )

    @override_settings(
        ADMIN_USERNAME='',
        ADMIN_PASSWORD='',
        ADMIN_EMAIL='',
    )
    @patch(
        'parcial.management.commands.crear_administrador.getpass',
        side_effect=['V3ryUnique-Passphrase-907!', 'V3ryUnique-Passphrase-907!'],
    )
    @patch('builtins.input', side_effect=['admin_cancha', 'admin@example.com'])
    def test_administrador_provisionado_puede_crear_canchas(
        self,
        input_mock,
        password_mock,
    ):
        call_command('crear_administrador', stdout=StringIO())
        administrador = get_user_model().objects.get(username='admin_cancha')
        self.client.force_login(administrador)

        respuesta = self.client.post(
            reverse('crear_cancha'),
            {
                'nombre': 'Cancha del administrador',
                'tipo': 'Futbol 5',
                'precio_hora': '50000.00',
                'activa': 'on',
            },
        )

        self.assertRedirects(respuesta, reverse('inicio'))
        self.assertTrue(
            Cancha.objects.filter(nombre='Cancha del administrador').exists()
        )


class FaseCeroYUnoTests(TestCase):
    """Estados de reserva, cancelación y calendario de franjas."""

    def setUp(self):
        self.manana = timezone.localdate() + timedelta(days=2)
        self.cancha = Cancha.objects.create(
            nombre='Cancha Central',
            tipo='Futbol 5',
            precio_hora=Decimal('50000.00'),
        )
        self.user_model = get_user_model()

    def crear_usuario(self, username='jugador'):
        usuario = self.user_model(username=username, email=f'{username}@example.com')
        usuario.password = 'secreto123'
        usuario.save()
        return usuario

    def crear_reserva(
        self,
        inicio=time(14, 0),
        fin=time(16, 0),
        usuario=None,
    ):
        return Reserva.objects.create(
            usuario=usuario,
            cancha=self.cancha,
            nombre_cliente='Cliente de prueba',
            telefono='3001234567',
            fecha=self.manana,
            hora_inicio=inicio,
            hora_fin=fin,
        )

    # --- Fase 0 ---------------------------------------------------------

    def test_el_modelo_rechaza_dos_reservas_solapadas(self):
        self.crear_reserva(time(14, 0), time(16, 0))

        with self.assertRaises(ValidationError):
            self.crear_reserva(time(15, 0), time(17, 0))

    def test_el_formulario_rechaza_una_hora_pasada_de_hoy(self):
        if timezone.localtime().time() == time(0, 0):
            self.skipTest('A las 00:00 no queda una hora anterior del mismo día.')

        form = ReservaForm(
            data={
                'cancha_id': str(self.cancha.id),
                'fecha': timezone.localdate().isoformat(),
                'hora_inicio': '00:00',
                'hora_fin': '01:00',
            },
            canchas=Cancha.objects.filter(activa=True),
        )

        self.assertFalse(form.is_valid())
        self.assertIn('hora_inicio', form.errors)

    def test_cancelar_libera_el_horario(self):
        usuario = self.crear_usuario()
        reserva = self.crear_reserva(usuario=usuario)

        self.client.force_login(usuario)
        respuesta = self.client.post(
            reverse('cancelar_reserva', args=[reserva.id])
        )

        self.assertRedirects(respuesta, reverse('lista_reservas'))
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, Reserva.Estado.CANCELADA)

        disponible = consultar_disponibilidad(
            self.cancha.id,
            self.manana,
            time(14, 0),
            time(15, 0),
        )
        self.assertTrue(disponible['disponible'])

    def test_no_se_puede_cancelar_una_reserva_ajena(self):
        dueno = self.crear_usuario('dueno')
        otro = self.crear_usuario('otro')
        reserva = self.crear_reserva(usuario=dueno)

        self.client.force_login(otro)
        self.client.post(reverse('cancelar_reserva', args=[reserva.id]))

        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, Reserva.Estado.CONFIRMADA)

    def test_el_registro_guarda_la_contrasena_en_texto_plano(self):
        respuesta = self.client.post(
            reverse('registro'),
            {
                'first_name': 'Nuevo',
                'last_name': 'Jugador',
                'username': 'nuevo',
                'email': 'nuevo@example.com',
                'telefono': '3001234567',
                'password1': 'clave2026',
                'password2': 'clave2026',
            },
        )

        self.assertRedirects(respuesta, reverse('inicio'))
        usuario = self.user_model.objects.get(username='nuevo')
        self.assertEqual(usuario.password, 'clave2026')
        self.assertTrue(self.client.login(username='nuevo', password='clave2026'))

    @override_settings(
        ADMIN_USERNAME='jefe',
        ADMIN_PASSWORD='cancha2026',
        ADMIN_EMAIL='jefe@example.com',
    )
    def test_el_administrador_se_crea_desde_el_entorno(self):
        call_command('crear_administrador', stdout=StringIO())

        jefe = self.user_model.objects.get(username='jefe')
        self.assertEqual(jefe.password, 'cancha2026')
        self.assertTrue(jefe.is_superuser)
        self.assertTrue(jefe.perfil.es_administrador)
        self.assertTrue(self.client.login(username='jefe', password='cancha2026'))

    # --- Fase 1 ---------------------------------------------------------

    def test_las_franjas_marcan_el_horario_ocupado(self):
        self.crear_reserva(time(14, 0), time(16, 0))

        franjas = {
            franja['inicio']: franja['estado']
            for franja in franjas_del_dia(self.cancha, self.manana)
        }

        self.assertEqual(franjas[time(13, 0)], 'libre')
        self.assertEqual(franjas[time(14, 0)], 'ocupado')
        self.assertEqual(franjas[time(15, 0)], 'ocupado')
        self.assertEqual(franjas[time(16, 0)], 'libre')

    def test_el_calendario_y_la_api_entregan_la_semana(self):
        self.crear_reserva(time(14, 0), time(16, 0))

        respuesta = self.client.get(
            reverse('calendario'),
            {'cancha': self.cancha.id},
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Horarios de la semana')

        api = self.client.get(
            reverse('api_disponibilidad'),
            {'cancha_id': self.cancha.id, 'semana': self.manana.isoformat()},
        )
        self.assertEqual(api.status_code, 200)

        datos = api.json()
        self.assertEqual(len(datos['dias']), 7)
        self.assertTrue(
            any(
                franja['estado'] == 'ocupado'
                for dia in datos['dias']
                for franja in dia['franjas']
            )
        )
