from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend


class AutenticacionSimpleBackend(BaseBackend):
    """Login comparando la contraseña tal como está en la tabla.

    Este proyecto guarda las contraseñas en texto plano porque es un trabajo
    de clase que nunca va a producción. Si algún día se despliega, hay que
    volver a `ModelBackend` y a `set_password()`.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return None

        try:
            usuario = UserModel.objects.get(
                **{f'{UserModel.USERNAME_FIELD}__iexact': username}
            )
        except UserModel.DoesNotExist:
            return None

        if usuario.is_active and usuario.password == password:
            return usuario
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
