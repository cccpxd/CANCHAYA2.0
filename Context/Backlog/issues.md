# Backlog del proyecto CANCHAYA2.0

Este archivo contiene una propuesta de issues para GitHub basada en la descripción del sistema, la estructura actual del proyecto y la idea principal: gestionar reservas de canchas, usuarios, torneos y reportes para un establecimiento deportivo.

---

## Issue 1: Registrar usuarios y autenticación de acceso

**Descripción**
Implementar el flujo de registro e inicio de sesión para estudiantes/usuarios del sistema. Los usuarios deben poder crear una cuenta con nombre, apellido, teléfono, correo, edad y contraseña, y luego iniciar sesión con correo y contraseña.

**Criterios de aceptación**
- Un usuario visitante puede crear una cuenta.
- Se valida que el correo sea único.
- Se valida que la contraseña cumpla con una política mínima.
- Un usuario registrado puede iniciar sesión correctamente.
- Un usuario autenticado puede cerrar sesión.
- Un usuario registrado puede eliminar su cuenta permanentemente.

**Labels sugeridas**
- `backend`
- `auth`
- `high-priority`

---

## Issue 2: Gestión de roles y permisos por tipo de usuario

**Descripción**
Definir y aplicar los permisos de cada tipo de usuario dentro del sistema: visitante, usuario registrado y administrador.

**Criterios de aceptación**
- Un visitante solo puede ver información pública.
- Un usuario registrado puede reservar canchas y participar en torneos.
- Un administrador puede gestionar canchas, usuarios y reservas.
- Cada vista y acción del sistema valida el rol del usuario.
- Los usuarios sin sesión no pueden acceder a funciones protegidas.

**Labels sugeridas**
- `backend`
- `roles`
- `security`

---

## Issue 3: Administrar canchas y registrar su precio de alquiler

**Descripción**
Crear la funcionalidad para que el administrador registre canchas con la información necesaria, incluyendo el valor del alquiler por hora.

**Criterios de aceptación**
- El administrador puede registrar una cancha con nombre, tipo, capacidad, estado y precio por hora.
- El precio del alquiler debe ser obligatorio al crear la cancha.
- El sistema almacena correctamente el estado de la cancha: disponible, ocupada o fuera de servicio.
- Las canchas registradas se muestran en la vista de inicio o en la administración.

**Labels sugeridas**
- `admin`
- `cancha`
- `crud`

---

## Issue 4: Validar disponibilidad de canchas y evitar conflictos de horario

**Descripción**
Evitar que dos reservas se solapen en la misma cancha y en el mismo horario.

**Criterios de aceptación**
- El sistema no permite crear dos reservas para la misma cancha en el mismo intervalo de tiempo.
- Se muestra un mensaje claro si la cancha ya está reservada.
- La validación funciona al momento de guardar la reserva.
- La lógica considera fecha, hora de inicio y hora de fin.

**Labels sugeridas**
- `backend`
- `validación`
- `reservation`

---

## Issue 5: Crear reservas de canchas desde la interfaz de usuario

**Descripción**
Permitir a los usuarios registrados reservar canchas indicando los datos del encuentro y los participantes necesarios.

**Criterios de aceptación**
- El usuario autenticado puede seleccionar fecha, cancha, hora de inicio y hora de finalización.
- El sistema registra los usuarios que participan en la reserva.
- El usuario puede indicar si habrá árbitro en el partido.
- La reserva queda visible en la lista de reservas del sistema.
- La reserva se asocia correctamente con la cancha y el usuario.

**Labels sugeridas**
- `frontend`
- `reservation`
- `user-story`

---

## Issue 6: Permitir completar equipos para partidos y buscar jugadores

**Descripción**
Añadir una funcionalidad que permita a los usuarios avisar que faltan jugadores para completar un equipo y que otros usuarios puedan unirse.

**Criterios de aceptación**
- Un usuario puede publicar una solicitud para completar equipo.
- Se registra la cantidad de jugadores necesarios.
- Otros usuarios registrados pueden participar en la solicitud.
- La lógica evita duplicar usuarios en el mismo equipo.
- Se puede visualizar el estado de la solicitud.

**Labels sugeridas**
- `feature`
- `team`
- `community`

---

## Issue 7: Registrar mantenimiento de canchas

**Descripción**
Permitir al administrador programar y registrar mantenimiento de las canchas para que queden fuera de servicio temporalmente.

**Criterios de aceptación**
- El administrador puede marcar una cancha como en mantenimiento.
- La cancha no está disponible para reservas durante ese periodo.
- El sistema registra la fecha y motivo del mantenimiento.
- El administrador puede reactivar la cancha cuando termine el mantenimiento.

**Labels sugeridas**
- `admin`
- `maintenance`
- `cancha`

---

## Issue 8: Crear sistema de torneos

**Descripción**
Implementar la funcionalidad de torneos dentro del sistema para que los administradores y usuarios puedan organizar competencias deportivas.

**Criterios de aceptación**
- El administrador puede crear torneos con descripción, reglas, premios, horarios y condiciones.
- Los usuarios pueden crear equipos con jugadores registrados.
- Los requisitos del torneo deben validarse antes de registrarse.
- Los equipos pueden inscribirse y visualizar su estado dentro del torneo.
- Se mantiene el registro de participantes y fechas.

**Labels sugeridas**
- `feature`
- `tournament`
- `admin`

---

## Issue 9: Implementar calificaciones y rankings de usuarios y canchas

**Descripción**
Crear un sistema de calificaciones para valorar la experiencia general de usuarios, canchas y servicio del establecimiento.

**Criterios de aceptación**
- Un usuario autenticado puede calificar la cancha.
- Se pueden evaluar aspectos como estado, servicio y comportamiento.
- El sistema guarda las valoraciones asociadas a la cancha o al usuario.
- Se pueden consultar rankings o promedios para comparar usuarios/canchas.
- La evaluación no permite calificaciones duplicadas por la misma persona en la misma reserva.

**Labels sugeridas**
- `feature`
- `rating`
- `analytics`

---

## Issue 10: Generar reportes de ocupación e ingresos diarios

**Descripción**
Desarrollar reportes para medir la ocupación de las canchas y los ingresos generados por día.

**Criterios de aceptación**
- El administrador puede ver un reporte de ocupación por cancha y por fecha.
- El sistema calcula ingresos acumulados por día.
- El reporte incluye reservas activas y completadas.
- Los datos se muestran de manera legible en la interfaz o en exportación básica.
- El reporte se basa en las reservas registradas en el sistema.

**Labels sugeridas**
- `analytics`
- `admin`
- `reporting`

---

## Issue 11: Mejorar la interfaz principal y flujo de navegación

**Descripción**
Mejorar la experiencia de usuario en la página principal y en los flujos principales del sistema para que sea claro y usable.

**Criterios de aceptación**
- La página principal muestra una navegación clara para visitante, usuario y administrador.
- El usuario puede acceder fácilmente a reservar, consultar reservas y cerrar sesión.
- La interfaz refleja el estado de las canchas disponibles o no disponibles.
- Las vistas tienen una estructura consistente con el diseño del proyecto.

**Labels sugeridas**
- `frontend`
- `ux`
- `enhancement`

---

## Issue 12: Validar y documentar la lógica de negocio del sistema

**Descripción**
Definir y documentar las reglas de negocio clave para asegurar que el sistema se comporte de manera consistente y sostenible.

**Criterios de aceptación**
- Se documenta la lógica de roles.
- Se documenta la validación de reservas solapadas.
- Se documenta el flujo de torneos y participación.
- Se documenta cómo se manejan canchas en mantenimiento.
- El equipo de desarrollo tiene una referencia central para futuras implementaciones.

**Labels sugeridas**
- `documentation`
- `business-rules`
- `planning`

---

## Recomendación de orden de implementación

1. Autenticación y roles
2. Gestión de canchas
3. Validación de reservas
4. Reserva de canchas
5. Mantenimiento y disponibilidad
6. Torneos
7. Rankings y calificaciones
8. Reportes de ocupación e ingresos

Esto permite construir la base del sistema primero y luego añadir funciones avanzadas como torneos, calificaciones y reportes.

---

## Nota para GitHub
Si deseas, puedes copiar cada issue como un “New issue” en GitHub, usando el título como referencia y el contenido del bloque como descripción. La estructura está preparada para ser pegada directamente en la plataforma.
