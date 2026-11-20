from getpass import getpass

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from ...models import Usuario


class Command(BaseCommand):
    help = (
        'Crea o actualiza el único administrador de Cancha Ya. '
        'Lee ADMIN_USERNAME, ADMIN_PASSWORD y ADMIN_EMAIL del .env; '
        'si faltan, los pide por consola.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--username', help='Sobrescribe ADMIN_USERNAME.')
        parser.add_argument('--password', help='Sobrescribe ADMIN_PASSWORD.')
        parser.add_argument('--email', help='Sobrescribe ADMIN_EMAIL.')

    def handle(self, *args, **options):
        username = options.get('username') or settings.ADMIN_USERNAME
        password = options.get('password') or settings.ADMIN_PASSWORD
        email = options.get('email') or settings.ADMIN_EMAIL

        if not username:
            username = input('Nombre de usuario: ').strip()
        if not email:
            email = input('Correo electrónico: ').strip()
        if not password:
            password = getpass('Contraseña: ')
            confirmation = getpass('Confirma la contraseña: ')
            if password != confirmation:
                raise CommandError('Las contraseñas no coinciden.')

        if not username:
            raise CommandError('El nombre de usuario es obligatorio.')
        if not password:
            raise CommandError('La contraseña es obligatoria.')

        user_model = get_user_model()
        candidato = user_model(username=username, email=email)

        try:
            validate_password(password, user=candidato)
        except ValidationError as error:
            raise CommandError(' '.join(error.messages)) from error

        with transaction.atomic():
            administrador = (
                Usuario.objects.select_related('user')
                .filter(rol=Usuario.Rol.ADMINISTRADOR)
                .first()
            )

            if administrador and administrador.user.username != username:
                raise CommandError(
                    'Ya existe un administrador con otro usuario: '
                    f'{administrador.user.username}.'
                )

            usuario = administrador.user if administrador else (
                user_model.objects.filter(username__iexact=username).first()
            )

            if usuario is None:
                usuario = user_model(username=username, email=email)

            usuario.email = email
            usuario.password = password  # Texto plano a propósito.
            usuario.is_staff = True
            usuario.is_superuser = True
            usuario.is_active = True
            usuario.save()

            if administrador is None:
                Usuario.objects.create(
                    user=usuario,
                    rol=Usuario.Rol.ADMINISTRADOR,
                )

        estado = 'actualizado' if administrador else 'creado'
        self.stdout.write(
            self.style.SUCCESS(
                f'Administrador {estado}: {username}'
            )
        )
