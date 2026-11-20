import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def cargar_env(ruta):
    """Carga un .env sencillo sin dependencias externas.

    Las variables que ya existen en el entorno tienen prioridad, así que
    `ADMIN_PASSWORD=otra python manage.py runserver` gana sobre el archivo.
    """
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding='utf-8').splitlines():
        linea = linea.strip()
        if not linea or linea.startswith('#') or '=' not in linea:
            continue
        clave, _, valor = linea.partition('=')
        os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


cargar_env(BASE_DIR / '.env')


def env_bool(nombre, por_defecto=False):
    valor = os.environ.get(nombre)
    if valor is None:
        return por_defecto
    return valor.strip().lower() in ('1', 'true', 'si', 'sí', 'yes', 'on')


def env_lista(nombre, por_defecto):
    valor = os.environ.get(nombre, por_defecto)
    return [elemento.strip() for elemento in valor.split(',') if elemento.strip()]


SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'parcial-local-development-key-change-before-deployment',
)
DEBUG = env_bool('DJANGO_DEBUG', True)
ALLOWED_HOSTS = env_lista(
    'DJANGO_ALLOWED_HOSTS',
    '127.0.0.1,localhost,testserver',
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'parcial.apps.ParcialConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'project.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'project.wsgi.application'
ASGI_APPLICATION = 'project.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'canchaYA'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'root'),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '5433'),
    }
}

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
LOGIN_URL = 'iniciar_sesion'
LOGIN_REDIRECT_URL = 'inicio'
LOGOUT_REDIRECT_URL = 'inicio'

# Las contraseñas se guardan tal cual en la tabla (proyecto de clase, sin
# producción). El backend compara el texto plano; no se usa el hasher de Django.
AUTHENTICATION_BACKENDS = [
    'parcial.backends.AutenticacionSimpleBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Administrador creado por `python manage.py crear_administrador`.
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', '')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', '')

# Calendario de disponibilidad.
DURACION_FRANJA_MINUTOS = int(os.environ.get('DURACION_FRANJA_MINUTOS', '60'))
HORARIO_APERTURA = os.environ.get('HORARIO_APERTURA', '06:00')
HORARIO_CIERRE = os.environ.get('HORARIO_CIERRE', '23:00')
DIAS_CALENDARIO = 7

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True
