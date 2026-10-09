# Descripción del sistema

## Idea principal
Este sistema es una plataforma de gestión deportiva para reservar canchas, administrar usuarios y organizar torneos. La finalidad es facilitar la reserva de espacios deportivos, controlar la disponibilidad, mantener la información del estado de las canchas y apoyar la organización de competencias entre usuarios registrados.

## Roles del sistema

### 1. Visitante
Un visitante es un usuario que no ha iniciado sesión. Solo puede consultar la información pública del sitio y navegar por la página, pero no puede realizar reservas ni acceder a funciones administrativas.

### 2. Usuario registrado
Un usuario registrado puede:
- crear su cuenta con los siguientes datos: nombre, apellido, número telefónico, correo personal, edad y contraseña;
- iniciar sesión con su correo y contraseña;
- cerrar sesión;
- eliminar su cuenta permanentemente;
- reservar una cancha disponible;
- ingresar los usuarios registrados con los que va a jugar;
- indicar la fecha, hora de inicio y hora de finalización del encuentro;
- decidir si otro usuario registrado actuará como árbitro del partido;
- participar en torneos y crear equipos siempre que todos los integrantes estén registrados y cumplan las condiciones del torneo;
- calificar el estado de la cancha, el servicio del establecimiento, la atención y el comportamiento del usuario en la cancha, permitiendo así clasificaciones y rankings dentro de la plataforma.

### 3. Administrador
Un administrador es un usuario con permisos de gestión del sistema y puede:
- iniciar sesión con correo y contraseña;
- registrar usuarios con nombre, apellido, número telefónico, correo personal, edad y contraseña;
- registrar canchas con el número máximo de jugadores, tipo de cancha, tipo de suelo y valor del alquiler;
- definir el estado de la cancha: disponible, ocupada o fuera de servicio;
- agendar mantenimiento a las canchas;
- crear torneos con descripción, reglas, premio, horarios y condiciones;
- gestionar reservas de canchas con usuarios registrados, fecha, hora y número de jugadores;
- generar reportes de ocupación e ingresos diarios.

## Reserva de canchas
Cuando un usuario registrado realiza una reserva, el sistema deberá tomar la información del usuario autenticado y registrar los siguientes datos:
- usuarios participantes;
- fecha del partido;
- hora de inicio;
- hora de finalización;
- cancha seleccionada;
- si se asignará un árbitro.

La plataforma debe evitar solapamientos de reservas en la misma cancha y en el mismo horario.

## Sistema de torneos
Los administradores pueden crear torneos con:
- descripción;
- reglas;
- premio;
- horarios;
- condiciones de participación.

Los usuarios registrados pueden:
- crear equipos;
- registrar a sus integrantes si todos están registrados y cumplen con los requisitos del torneo;
- inscribirse en la competencia según las condiciones establecidas por el administrador.

## Sistema de calificaciones y rankings
El sistema permite evaluar diferentes aspectos relacionados con la experiencia deportiva, por ejemplo:
- estado de la cancha;
- servicio del establecimiento;
- calidad del servicio brindado;
- comportamiento y rendimiento de los usuarios.

Estas valoraciones pueden servir para generar rankings y mejorar la experiencia dentro de la plataforma.

## Reglas de negocio principales
- Un visitante no puede reservar ni gestionar contenido.
- Un usuario debe estar registrado para hacer reservas o participar en torneos.
- El administrador debe registrar el valor del alquiler de cada cancha junto con los demás datos de la cancha.
- No se pueden registrar dos reservas en la misma cancha y horario.
- El sistema debe mostrar reportes de ocupación y de ingresos diaros.
- Las canchas pueden presentarse en varios estados: disponible, ocupada o fuera de servicio.

## Conclusión
La idea principal del sistema es convertirlo en una plataforma integral para la gestión deportiva de canchas, reservas, usuarios, mantenimiento, torneos y reportes, con un enfoque claro en la organización de actividades deportivas y en la administración eficiente del establecimiento.