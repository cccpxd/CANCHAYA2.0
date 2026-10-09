# Proyecto CANCHAYA2.0 - Backlog

## 1. Descripción general del proyecto
CANCHAYA2.0 es un sistema web para gestionar reservas y administración de canchas deportivas. El objetivo principal es permitir que usuarios registrados puedan reservar canchas, consultar disponibilidad, completar equipos, participar en torneos y acceder a reportes del establecimiento. También incluye un rol administrativo para gestionar canchas, usuarios, mantenimiento, reservas y reportes de ocupación e ingresos.

La aplicación está pensada para simplificar la coordinación de partidos, evitar conflictos de horarios y centralizar la operación del establecimiento deportivo en una sola plataforma.

## 2. Objetivo principal del sistema
Facilitar la gestión de reservas deportivas, la organización de torneos, la administración de canchas y la experiencia del usuario dentro de una plataforma web centralizada.

## 3. Roles del sistema
- Visitante: puede consultar la información pública, pero no puede reservar ni acceder a funciones administrativas.
- Usuario registrado: puede reservar canchas, gestionar reservas, completar equipos, participar en torneos y calificar la experiencia.
- Administrador: puede registrar usuarios, gestionar canchas, programar mantenimiento, crear torneos y consultar reportes.

## 4. Reglas de negocio clave
- Un visitante no puede acceder a funcionalidades restringidas.
- Un usuario debe registrarse para reservar canchas.
- Cada cancha debe tener un precio de alquiler obligatorio.
- No se permiten reservas superpuestas en la misma cancha y horario.
- Cada reserva requiere fecha, hora de inicio, hora de fin y cancha.
- Las canchas pueden estar disponibles, ocupadas o fuera de servicio.
- Los torneos requieren reglas, condiciones, premios y horarios definidos por el administrador.
- El sistema debe permitir reportes de ocupación e ingresos diarios.

## 5. Backlog de funcionalidades

### Epic 1: Autenticación y gestión de usuarios
- Registrar usuarios con nombre, apellido, teléfono, correo, edad y contraseña.
- Iniciar sesión con correo y contraseña.
- Cerrar sesión.
- Eliminar cuenta permanentemente.
- Gestionar permisos por rol.

### Epic 2: Administración de canchas
- Registrar canchas con nombre, tipo, capacidad, estado y valor del alquiler.
- Definir el estado de la cancha.
- Programar mantenimiento.
- Visualizar el listado de canchas disponibles.

### Epic 3: Reservas y disponibilidad
- Reservar una cancha por fecha y horario.
- Validar que no existan conflictos de disponibilidad.
- Registrar participantes y árbitro.
- Mostrar reservas en la lista del sistema.

### Epic 4: Equipos y torneos
- Crear equipos para partidos.
- Completar equipos con usuarios registrados.
- Crear torneos con reglas, condiciones y premios.
- Inscribir equipos en torneos.

### Epic 5: Calificaciones y rankings
- Calificar canchas y servicio.
- Valorar comportamiento y rendimiento de usuarios.
- Generar rankings por desempeño o experiencia.

### Epic 6: Reportes y administración
- Generar reportes de ocupación diaria.
- Calcular ingresos por día y por cancha.
- Consultar estadísticas operativas del sistema.

## 6. Issues del proyecto

### Issue 1: Registrar usuarios y autenticación de acceso
**Descripción:** Implementar el flujo de registro e inicio de sesión para usuarios del sistema.

**Criterios de aceptación:**
- Un visitante puede crear una cuenta.
- El correo debe ser único.
- La contraseña debe cumplir una política mínima.
- Un usuario registrado puede iniciar sesión.
- Un usuario autenticado puede cerrar sesión.
- Un usuario puede eliminar su cuenta permanentemente.

### Issue 2: Gestión de roles y permisos por tipo de usuario
**Descripción:** Definir permisos para visitante, usuario registrado y administrador.

**Criterios de aceptación:**
- El visitante solo puede ver información pública.
- El usuario registrado puede reservar canchas y participar en torneos.
- El administrador puede gestionar canchas, usuarios y reservas.
- Las vistas validan el rol del usuario.

### Issue 3: Administrar canchas y registrar su precio de alquiler
**Descripción:** Crear la funcionalidad para registrar canchas con sus datos principales y el valor del alquiler por hora.

**Criterios de aceptación:**
- El administrador puede registrar una cancha con nombre, tipo, capacidad, estado y precio por hora.
- El precio del alquiler es obligatorio.
- El estado puede ser disponible, ocupada o fuera de servicio.
- Las canchas se muestran en la vista del sistema.

### Issue 4: Validar disponibilidad de canchas y evitar conflictos de horario
**Descripción:** Evitar que dos reservas se solapen en la misma cancha y horario.

**Criterios de aceptación:**
- El sistema impide una reserva duplicada en la misma cancha y horario.
- Se muestra un mensaje de conflicto si está ocupada.
- La validación considera fecha, inicio y fin.

### Issue 5: Crear reservas de canchas desde la interfaz de usuario
**Descripción:** Permitir a los usuarios registrados reservar canchas con los datos del encuentro.

**Criterios de aceptación:**
- El usuario puede seleccionar fecha, cancha, hora de inicio y finalización.
- Se registran los participantes del partido.
- Se puede indicar si habrá árbitro.
- La reserva queda visible en la lista.

### Issue 6: Permitir completar equipos para partidos y buscar jugadores
**Descripción:** Permitir que los usuarios publiquen la necesidad de completar un equipo.

**Criterios de aceptación:**
- Un usuario puede publicar una solicitud para completar equipo.
- Se registra la cantidad de jugadores necesarios.
- Otros usuarios pueden unirse.
- No se duplican jugadores en el mismo equipo.

### Issue 7: Registrar mantenimiento de canchas
**Descripción:** Programar mantenimiento para que la cancha quede temporalmente fuera de servicio.

**Criterios de aceptación:**
- El administrador marca la cancha como en mantenimiento.
- La cancha no está disponible para reservas.
- Se registra la fecha y motivo del mantenimiento.

### Issue 8: Crear sistema de torneos
**Descripción:** Implementar la funcionalidad de torneos.

**Criterios de aceptación:**
- El administrador crea torneos con descripción, reglas, premios y condiciones.
- Los usuarios crean equipos.
- Los equipos se inscriben según los requisitos del torneo.

### Issue 9: Implementar calificaciones y rankings de usuarios y canchas
**Descripción:** Permitir evaluaciones de experiencia y rendimiento deportivo.

**Criterios de aceptación:**
- El usuario puede calificar la cancha y servicio.
- Se registran valoraciones y promedios.
- Se pueden generar rankings.

### Issue 10: Generar reportes de ocupación e ingresos diarios
**Descripción:** Mostrar estadísticas para analizar ocupación e ingresos.

**Criterios de aceptación:**
- El administrador puede ver reportes por cancha y fecha.
- El sistema calcula ingresos por día.
- Se incluye la ocupación real de cada cancha.

### Issue 11: Mejorar la interfaz principal y flujo de navegación
**Descripción:** Mejorar la usabilidad general de la aplicación.

**Criterios de aceptación:**
- La navegación es clara para visitantes, usuarios y administradores.
- Las canchas muestran su estado facilmente.
- El flujo principal es simple y consistente.

### Issue 12: Validar y documentar la lógica de negocio del sistema
**Descripción:** Documentar las reglas operativas del sistema.

**Criterios de aceptación:**
- Se documenta el flujo de roles.
- Se documenta la validación de reservas.
- Se documentan torneos, mantenimiento y reportes.

## 7. Recomendación de priorización
1. Autenticación y roles.
2. Administración de canchas.
3. Validación de disponibilidad y reservas.
4. Mantenimiento.
5. Torneos.
6. Rankings y calificaciones.
7. Reportes de ingresos y ocupación.

## 8. Estado actual del proyecto
El proyecto ya tiene una base funcional con modelos de canchas y reservas, además de vistas iniciales para inicio y listado de reservas. La arquitectura actual permite continuar con autenticación, permisos, gestion de usuarios y mejoras en la lógica de negocio.

## 9. Siguiente paso sugerido
Implementar primero la autenticación y gestión de roles, luego la creación y validación de canchas y reservas, para construir la base sólida del sistema antes de agregar torneos, rankings y reportes avanzados.
