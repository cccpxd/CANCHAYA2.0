from getpass import getpass

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction

from ...models import Usuario


class Command(BaseCommand):
    help = 'Crea el único administrador de Cancha Ya.'

    def handle(self, *args, **options):
        if Usuario.objects.filter(rol=Usuario.Rol.ADMINISTRADOR).exists():
            raise CommandError('Ya existe un administrador.')

        username = input('Nombre de usuario: ').strip()
        email = input('Correo electrónico: ').strip()
        password = getpass('Contraseña: ')
        confirmation = getpass('Confirma la contraseña: ')

        if not username:
            raise CommandError('El nombre de usuario es obligatorio.')
        if password != confirmation:
            raise CommandError('Las contraseñas no coinciden.')

        user_model = get_user_model()
        candidato = user_model(username=username, email=email)
        try:
            validate_password(password, user=candidato)
            with transaction.atomic():
                user = user_model.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                )
                Usuario.objects.create(
                    user=user,
                    rol=Usuario.Rol.ADMINISTRADOR,
                )
        except (IntegrityError, ValidationError, ValueError) as error:
            raise CommandError(str(error)) from error

        self.stdout.write(self.style.SUCCESS('Administrador creado correctamente.'))