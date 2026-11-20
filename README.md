# Cancha Ya

Sistema de reservas para canchas sintéticas hecho con Django 5 y PostgreSQL.
Consulta la disponibilidad de la semana, reserva un horario y cancélalo si el
partido se cae.

## Requisitos

- Python 3.12 o superior
- Docker (para el PostgreSQL de `compose.yaml`) o un PostgreSQL propio

## Puesta en marcha

```bash
# 1. Base de datos
docker compose up -d db

# 2. Entorno de Python
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS
pip install -r requirements.txt

# 3. Configuración
copy .env.example .env          # Windows
# cp .env.example .env          # Linux / macOS

# 4. Tablas y administrador
python manage.py migrate
python manage.py crear_administrador
python manage.py cargar_demo     # opcional: canchas y reservas de ejemplo
python manage.py runserver
```

Abre `http://127.0.0.1:8000`.

## Variables de entorno (`.env`)

| Variable | Para qué sirve |
|---|---|
| `DJANGO_SECRET_KEY` | Clave de Django. |
| `DJANGO_DEBUG` | `True` en desarrollo. |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos, separados por coma. |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Conexión a PostgreSQL. Coinciden con `compose.yaml`. |
| `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `ADMIN_EMAIL` | Cuenta que crea `crear_administrador` sin preguntar nada. |
| `DURACION_FRANJA_MINUTOS` | Tamaño de cada franja del calendario (60 por defecto). |
| `HORARIO_APERTURA`, `HORARIO_CIERRE` | Horario del día que se muestra en el calendario. |

El `.env` no se sube al repositorio.

## Contraseñas en texto plano

Este es un proyecto de clase y **no va a producción**: los usuarios guardan la
contraseña tal cual en la tabla y `AutenticacionSimpleBackend` la compara sin
hash. Si algún día se despliega, hay que volver a `ModelBackend` y a
`set_password()`.

## Qué incluye

- Registro, inicio y cierre de sesión con dos roles: cliente y administrador.
- Canchas con tipo, precio por hora y activar/desactivar.
- Calendario semanal de disponibilidad por cancha, con las franjas libres
  enlazadas al formulario de reserva.
- La API `GET /api/disponibilidad/` refresca la grilla sin recargar la página.
- Una reserva no se puede solapar con otra de la misma cancha: se valida en el
  modelo y con bloqueo de la cancha al guardar.
- Estados de reserva (confirmada/cancelada) y cancelación con liberación del
  horario.
- No se permiten fechas pasadas ni horas que ya pasaron hoy.

## Rutas

| Ruta | Pantalla |
|---|---|
| `/` | Inicio, canchas y próximos cupos |
| `/calendario/` | Grilla semanal de disponibilidad |
| `/reservar/` | Formulario de reserva |
| `/reservas/` | Reservas del usuario (todas si es administrador) |
| `/disponibilidad/` | Consulta puntual de un rango de horas |
| `/registro/`, `/iniciar-sesion/` | Cuenta |

## Pruebas

```bash
python manage.py test parcial
```

El suite cubre disponibilidad, solapamientos, permisos, cancelación,
contraseña en texto plano, el calendario y la API.
