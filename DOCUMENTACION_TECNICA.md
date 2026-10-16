# Documentación técnica de Cancha Ya

## 1. Propósito y alcance

Cancha Ya es una aplicación web construida con Django para consultar canchas deportivas, crear reservas y revisar las reservas existentes. El proyecto también contiene un modelo y una página para torneos, aunque esa parte todavía está incompleta.

Esta guía describe el código que existe actualmente. El README y los documentos de `Context/` mencionan ideas como pagos, notificaciones, equipos y reportes; esas ideas no deben confundirse con funciones ya implementadas.

## 2. Tecnologías y dependencias

### Python y paquetes

Las dependencias directas declaradas están en [`requirements.txt`](requirements.txt):

| Paquete | Función en este proyecto |
|---|---|
| `Django` | Framework web: rutas, vistas, ORM, modelos, formularios, administración, mensajes, plantillas, pruebas y migraciones. |
| `django-environ` | Lee variables de entorno y el archivo `.env`; también convierte valores a tipos como booleanos y listas. Se importa como `environ`. |
| `psycopg[binary]` | Controlador PostgreSQL utilizado por el backend `django.db.backends.postgresql` de Django. El código del proyecto no lo importa directamente. |

`asgiref`, `sqlparse` y `tzdata` también aparecen fijados en requisitos; son dependencias del entorno Django y no se importan directamente desde el código de la aplicación.

### Módulos importados

| Import | Procedencia y uso |
|---|---|
| `os` | Biblioteca estándar. Permite definir variables de entorno en `manage.py`, `config/asgi.py` y `config/wsgi.py`. |
| `sys` | Biblioteca estándar. Proporciona los argumentos con que se invoca `manage.py`. |
| `pathlib.Path` | Biblioteca estándar. Construye rutas de archivos y `BASE_DIR` en `config/settings.py`. |
| `datetime.date`, `datetime.time` | Biblioteca estándar. Crea valores de fecha y hora en las pruebas. |
| `django.core.management.execute_from_command_line` | Ejecuta comandos como `runserver`, `migrate`, `test` y `createsuperuser`. Se importa dentro de `main()` en `manage.py`. |
| `django.core.asgi.get_asgi_application` | Crea el punto de entrada ASGI para servidores compatibles. |
| `django.core.wsgi.get_wsgi_application` | Crea el punto de entrada WSGI para servidores compatibles. |
| `django.contrib.admin` | Habilita y configura el panel administrativo. |
| `django.urls.path`, `django.urls.include` | Declaran rutas y conectan las rutas de la aplicación con las del proyecto. |
| `django.apps.AppConfig` | Clase base para la configuración de la aplicación `reservas`. |
| `django.db.models` | API del ORM para definir modelos, campos, relaciones, opciones y consultas. |
| `django.db.models.Q` | Construye condiciones combinadas para buscar intervalos de reservas superpuestos. Se importa localmente en `Cancha.esta_disponible()`. |
| `django.db.transaction` | Proporciona transacciones de base de datos; `transaction.atomic` mantiene una operación como unidad. |
| `django.forms` | API para construir y validar formularios HTML. |
| `django.contrib.messages.messages` | Añade mensajes temporales, por ejemplo, la confirmación de una reserva. |
| `django.shortcuts.redirect`, `django.shortcuts.render` | `render` produce una respuesta usando una plantilla; `redirect` devuelve al navegador a otra ruta. |
| `django.test.TestCase` | Base de las pruebas automatizadas con una base de datos aislada. |
| `django.db.migrations`, `django.db.models` | API declarativa utilizada por los archivos de migración para evolucionar el esquema. |
| `reservas.models` | Importación interna de modelos desde formularios y administración. |
| `reservas.forms.ReservaForm` | Importación interna del formulario desde las vistas. |
| `reservas.views` | Importación interna de vistas desde las rutas de la aplicación. |

## 3. Organización del proyecto

- [`manage.py`](manage.py): punto de entrada de la línea de comandos de Django.
- [`config/`](config/): configuración general del proyecto, URL raíz y puntos de entrada ASGI/WSGI.
- [`reservas/`](reservas/): aplicación principal con modelos, formulario, vistas, administración, rutas, migraciones, pruebas, CSS y plantillas.
- [`docker-compose.yml`](docker-compose.yml): servicios de desarrollo PostgreSQL y pgAdmin; no crea un contenedor para Django.
- [`.env.example`](.env.example): muestra qué variables de entorno necesita la configuración. No es el archivo privado `.env`.
- [`db.sqlite3`](db.sqlite3): archivo SQLite presente en el repositorio. La configuración actual de Django utiliza PostgreSQL, no este archivo.

Los archivos `__init__.py` identifican directorios como paquetes Python. Los `__init__.py` de `config`, `reservas` y `reservas/migrations` no añaden lógica propia.

## 4. Símbolos, funciones y métodos

### `manage.py`

- `main()`: fija `DJANGO_SETTINGS_MODULE` en `config.settings`, importa `execute_from_command_line` y le pasa `sys.argv`. El bloque `if __name__ == '__main__'` llama a esta función al ejecutar `python manage.py ...`.

### Configuración `config`

- `config/settings.py`: módulo de valores de configuración, no define funciones propias. Calcula `BASE_DIR`, carga `.env`, configura aplicaciones, middleware, plantillas, base de datos, validadores de contraseña, idioma, zona horaria, archivos estáticos y claves primarias. Usa `django-environ` para leer variables.
- `config/urls.py`: define `urlpatterns`; envía `/admin/` al panel integrado de Django e incluye las rutas de `reservas` desde `/`.
- `config/asgi.py`: define `application` mediante `get_asgi_application()`, el punto de entrada para servidores ASGI.
- `config/wsgi.py`: define `application` mediante `get_wsgi_application()`, el punto de entrada para servidores WSGI.

### Aplicación `reservas`

#### `reservas/apps.py`

- `ReservasConfig(AppConfig)`: declara el nombre de la aplicación y el tipo de clave primaria predeterminado. Django utiliza esta configuración al cargar `reservas`.

#### `reservas/models.py`

- `Cancha`: representa una cancha deportiva.
  - `Tipo(models.TextChoices)`: opciones de tipo disponibles, fútbol 5 y vóley playa.
  - `Meta`: ordena los registros por `nombre`.
  - `__str__()`: devuelve el nombre de la cancha para representarla como texto.
  - `esta_disponible(fecha, hora_inicio, hora_fin, excluir_reserva_id=None)`: busca reservas de esta cancha en la misma fecha que se crucen con el intervalo solicitado. Devuelve `True` si no hay ninguna. Si se pasa `excluir_reserva_id`, no considera esa reserva, lo que permite validar una reserva existente al editarla.
- `Reserva`: almacena cancha, nombre del cliente, teléfono, fecha, hora de inicio, hora de fin y fecha de creación. Su `ForeignKey` a `Cancha` usa `related_name='reservas'`, que permite consultar las reservas relacionadas desde la cancha.
  - `Meta`: ordena las reservas por fecha y hora de inicio.
  - `__str__()`: devuelve una representación con cancha, fecha y hora inicial.
- `Torneos`: almacena nombre, fechas de inicio/fin y una relación muchos-a-muchos con canchas.
  - `Meta`: ordena por fecha de inicio.
  - `__str__()`: devuelve el nombre del torneo.

Los intervalos se comparan como intervalos semiabiertos: una reserva existente se considera conflictiva cuando su inicio es anterior al fin solicitado y su fin es posterior al inicio solicitado. Por ello se permiten reservas consecutivas, por ejemplo, una termina a las 15:00 y otra empieza a las 15:00. No se exige un minuto de separación.

#### `reservas/forms.py`

- `ReservaForm(forms.ModelForm)`: formulario ligado al modelo `Reserva`.
  - `Meta`: define los campos editables y widgets HTML de fecha y hora (`type=date` y `type=time`).
  - `__init__(*args, **kwargs)`: inicializa el formulario base y limita el selector a canchas activas.
  - `clean()`: valida el conjunto de campos. Rechaza que la hora de inicio sea igual o posterior a la final. Para una solicitud con horas coherentes, bloquea la fila de la cancha mediante `select_for_update()` y consulta `Cancha.esta_disponible()`. El bloqueo ayuda a serializar solicitudes concurrentes cuando se ejecuta dentro de la transacción de la vista. Si hay solapamiento, agrega un error general al formulario.

#### `reservas/views.py`

- `inicio(request)`: consulta canchas activas y renderiza `reservas/inicio.html` con ellas.
- `crear_reserva(request)`: está decorada con `@transaction.atomic`, por lo que el procesamiento de una solicitud ocurre dentro de una transacción. En `POST`, crea y valida `ReservaForm`; si es válido, guarda la reserva, agrega un mensaje de éxito y redirige a la lista. En `GET`, muestra un formulario vacío. Si la validación falla, vuelve a renderizar el formulario con sus errores.
- `lista_reservas(request)`: consulta todas las reservas y usa `select_related('cancha')` para cargar también la cancha relacionada en la misma consulta eficiente; renderiza `reservas/lista.html`.
- `lista_torneos(request)`: consulta todos los torneos y los pasa a `reservas/torneos.html`. La plantilla actual todavía no recorre ni muestra ese contexto.

#### `reservas/urls.py`

- `app_name = 'reservas'`: define el espacio de nombres para usar nombres de ruta como `reservas:inicio` desde plantillas y vistas.
- `urlpatterns`: enlaza cada ruta con una vista. No contiene funciones propias.

#### `reservas/admin.py`

- `CanchaAdmin(admin.ModelAdmin)`: personaliza la tabla de canchas con nombre, tipo, precio y estado; añade filtros por tipo y estado. El decorador `@admin.register(Cancha)` registra el modelo.
- `ReservaAdmin(admin.ModelAdmin)`: muestra cancha, cliente, fecha y horas; añade filtros por cancha y fecha. El decorador `@admin.register(Reserva)` registra el modelo.
- `Torneos` no está registrado aquí, por lo que no aparece en el panel administrativo actual.

#### `reservas/test.py`

- `ReservaReglaTestCase(TestCase)`: agrupa pruebas automatizadas del formulario.
- `setUp()`: crea una cancha y define una fecha común para las pruebas.
- `test_crear_reserva_valida()`: comprueba que datos válidos pasan la validación.
- `test_reserva_invalida_hora_retrograda()`: comprueba que una hora final anterior a la inicial se rechaza y genera un error en `hora_fin`.
- `test_reserva_solapada()`: crea una reserva y comprueba que otra que se cruza en horario se rechaza.

### Migraciones

- `reservas/migrations/0001_initial.py`: crea las tablas iniciales de canchas y reservas.
- `reservas/migrations/0002_torneos.py`: crea la tabla de torneos y su relación muchos-a-muchos con canchas.
- En cada archivo, `Migration` es una descripción declarativa que Django interpreta; `dependencies` indica el orden requerido y `operations` enumera cambios de esquema. No son funciones de negocio que se invoquen manualmente.

## 5. Rutas y páginas

| URL | Nombre | Vista | Resultado |
|---|---|---|---|
| `/` | `reservas:inicio` | `inicio` | Inicio con canchas activas. |
| `/reservar/` | `reservas:crear` | `crear_reserva` | Formulario de reserva por `GET`; validación y guardado por `POST`. |
| `/reservas/` | `reservas:lista` | `lista_reservas` | Lista todas las reservas registradas. |
| `/torneos/` | `reservas:torneos` | `lista_torneos` | Página de torneos actualmente estática/incompleta. |
| `/admin/` | Administración de Django | `admin.site.urls` | Administración de canchas y reservas para usuarios autorizados. |

### Plantillas

- `reservas/templates/reservas/base.html`: estructura HTML común, navegación, mensajes de Django y carga del CSS compartido.
- `reservas/templates/reservas/inicio.html`: muestra la presentación y tarjetas de canchas activas. El texto indica “disponibles hoy”, pero la vista solo filtra por cancha activa; no calcula disponibilidad para el día.
- `reservas/templates/reservas/reserva_form.html`: muestra los campos, errores y token CSRF. Un JavaScript desactiva el botón al enviar y cambia el texto para reducir envíos repetidos desde la interfaz. La validación transaccional del servidor es la protección adicional ante solicitudes concurrentes.
- `reservas/templates/reservas/lista.html`: presenta cancha, tipo, fecha, intervalo, nombre y teléfono de cada reserva.
- `reservas/templates/reservas/torneos.html`: actualmente muestra un botón deshabilitado y un mensaje fijo; no usa la lista de torneos que entrega la vista.
- `reservas/static/reservas/styles.css`: define los estilos comunes y el diseño adaptable de las páginas.

## 6. Flujo de creación de una reserva

1. El navegador solicita `/reservar/` mediante `GET`.
2. `crear_reserva()` muestra `ReservaForm`; el selector solo ofrece canchas activas.
3. El navegador envía los campos mediante `POST` junto con el token CSRF.
4. La vista abre una transacción. `ReservaForm.clean()` comprueba el orden de las horas y bloquea la fila de la cancha antes de consultar conflictos.
5. `Cancha.esta_disponible()` busca una reserva de la misma cancha/fecha cuyo intervalo se cruce con el solicitado.
6. Si no existe conflicto, Django guarda una fila `Reserva`, muestra un mensaje y redirige a `/reservas/`.
7. Si la información no es válida o el horario está ocupado, se vuelve a mostrar el formulario con errores.

El botón deshabilitado es una ayuda de interfaz, no una garantía del servidor. La transacción y el bloqueo son importantes para solicitudes que puedan llegar a la vez. La protección descrita depende del backend PostgreSQL usado por el proyecto; no representa una restricción de exclusión permanente en la base de datos y no cubre escrituras que eviten este flujo Django.

## 7. Configuración y ejecución local

### Variables de entorno

`config/settings.py` carga un archivo `.env` ubicado en la raíz del proyecto con `django-environ`. Entre las variables configurables están el nombre, usuario, contraseña, host y puerto de PostgreSQL, además de los parámetros de pgAdmin y los ajustes de Django como `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS`.

- `.env.example` es una plantilla de configuración para desarrollo; no se debe usar como conjunto de credenciales de producción.
- `.env` contiene valores locales y está excluido por `.gitignore`; no debe subirse a GitHub.
- La configuración actual tiene valores de respaldo de desarrollo para la clave secreta y la base de datos. En producción se deben reemplazar con secretos externos seguros, desactivar `DEBUG` y configurar `ALLOWED_HOSTS`.

### Arranque en Windows PowerShell

Desde la carpeta `CANCHAYA2.0`:

```powershell
.\.venv\Scripts\Activate.ps1
docker compose up -d db pgadmin
python manage.py migrate
python manage.py runserver
```

La aplicación se sirve en `http://127.0.0.1:8000/`. pgAdmin se publica en el puerto indicado por `PGADMIN_PORT` (por defecto, `5050`); PostgreSQL se publica en el puerto indicado por `DB_PORT` (por defecto, `5433` en el host y `5432` dentro de Docker). Para usar el panel se inicia sesión con las variables configuradas para pgAdmin y se registra una conexión PostgreSQL hacia el servicio de Compose `db` en el puerto interno `5432`.

Otros comandos útiles:

```powershell
python manage.py test reservas
python manage.py createsuperuser
python manage.py check
```

El usuario administrador se crea con `createsuperuser`; luego puede iniciar sesión en `/admin/`.

### Docker Compose

[`docker-compose.yml`](docker-compose.yml) define:

- `db`: PostgreSQL 16 Alpine, con volumen persistente y healthcheck basado en `pg_isready`.
- `pgadmin`: interfaz web de administración, dependiente de que `db` esté saludable, con su propio volumen.

Compose no ejecuta `manage.py` ni construye la aplicación Django. La aplicación se ejecuta aparte desde el entorno Python local.

## 8. Migraciones y almacenamiento

Las migraciones describen cambios al esquema, no copias completas de los datos. `python manage.py migrate` aplica las que aún faltan.

Aunque el repositorio contiene `db.sqlite3`, `DATABASES['default']` está configurado con el motor PostgreSQL. Por tanto, las reservas creadas por la configuración normal se guardan en PostgreSQL del contenedor y no necesariamente en `db.sqlite3`. El archivo SQLite está versionado en Git; antes de compartir el repositorio, verifica que no contenga datos personales que no deban publicarse.

## 9. Consideraciones importantes y trabajo pendiente

- **Privacidad:** la vista `/reservas/` es pública y muestra nombre y teléfono del cliente. Restringe el acceso o elimina/anonimiza esos datos antes de poner el sitio a disposición pública.
- **Seguridad:** no usar valores de desarrollo ni `DEBUG=True` en producción. No publicar `.env`, contraseñas reales ni claves secretas.
- **Torneos:** existe modelo, migración y vista, pero faltan administración, formulario, alta/edición y una plantilla que renderice los registros.
- **Disponibilidad:** la validación comprueba solapamientos para la misma cancha y fecha. No comprueba horario comercial, duración máxima ni que la fecha sea futura.
- **Reservas duplicadas:** la interfaz deshabilita el botón después de enviar y la vista serializa la validación con una transacción y bloqueo de cancha. No hay restricción de exclusión en la base que cubra escrituras ajenas al flujo de la vista.
- **Pruebas:** hay pruebas de validación del formulario, pero no pruebas automatizadas de concurrencia, permisos, rutas o presentación de las plantillas.
- **Idioma y zona horaria:** el contenido visible está en español, mientras `LANGUAGE_CODE` es `en-us` y `TIME_ZONE` es `UTC`; revisar estos valores si la aplicación se usará en una zona local específica.
- **Alcance futuro:** pagos, notificaciones, publicación para buscar jugadores, incorporación de jugadores, árbitros, calificaciones, rankings y reportes se describen como objetivos, pero no están implementados en los módulos actuales.

## 10. Cómo mantener esta guía

Cuando se añadan modelos, rutas, formularios, vistas o dependencias, actualizar las secciones correspondientes y ejecutar las pruebas. Mantener separadas las funciones presentes de las ideas futuras evita que la documentación prometa capacidades que el sistema aún no ofrece.
