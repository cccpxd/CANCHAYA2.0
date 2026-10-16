# Parcial 2: disponibilidad de canchas

## Regla seleccionada

Al solicitar una reserva, una cancha está disponible si no existe otra reserva para esa misma cancha y fecha cuyo horario se cruce con el intervalo solicitado. Si el horario está ocupado, la reserva debe rechazarse.

La regla se implementa en `Cancha.esta_disponible()` en `reservas/models.py`. El formulario `ReservaForm.clean()` en `reservas/forms.py` comprueba que la hora final sea posterior a la inicial y consulta la disponibilidad de la cancha antes de aceptar los datos.

## Entradas y salidas esperadas

| Entrada | Descripción |
|---|---|
| `fecha` | Día para el que se solicita la reserva. |
| `hora_inicio` | Hora de inicio solicitada. |
| `hora_fin` | Hora de finalización solicitada. |
| `excluir_reserva_id` | Identificador opcional de una reserva existente que no debe contarse como conflicto al editarla. |

La función devuelve `True` cuando no encuentra un cruce de horario y `False` cuando ya hay una reserva que se superpone. La comparación usa intervalos semiabiertos: si una reserva termina exactamente cuando empieza la siguiente, no se consideran solapadas. La función de disponibilidad presupone que el intervalo tiene horas coherentes; el formulario rechaza intervalos cuya hora inicial sea igual o posterior a la hora final.

## Casos probados

Las pruebas automatizadas están en `reservas/test.py`, dentro de `ReservaReglaTestCase`.

| Prueba | Datos relevantes | Resultado esperado |
|---|---|---|
| `test_crear_reserva_valida` | Cancha sin reservas ese día, de 14:00 a 15:00. | El formulario es válido. |
| `test_reserva_invalida_hora_retrograda` | De 16:00 a 15:00. | El formulario es inválido y presenta error en `hora_fin`. |
| `test_reserva_solapada` | Ya existe una reserva de 14:00 a 16:00; se solicita de 15:00 a 17:00. | El formulario es inválido por conflicto de horario. |

Estos tres casos cumplen el rango de tres a cinco pruebas indicado en la actividad e incluyen un dato inválido y una colisión de horarios.

## Organización y responsabilidad única

La comprobación de conflictos pertenece a `Cancha.esta_disponible()`, junto al modelo que conoce sus reservas. `ReservaForm` se ocupa de validar los datos enviados por el usuario y delega la pregunta de disponibilidad al modelo. Así se evita que el formulario tenga que construir por sí mismo la consulta de solapamientos y se mantiene más clara la responsabilidad de cada parte.

## Ejecución de las pruebas

Desde la raíz del proyecto, con PostgreSQL iniciado, ejecutar:

```powershell
python manage.py test reservas -v 2
```

Resultado verificado en el entorno de desarrollo: Django encontró 3 pruebas, el chequeo del sistema no reportó problemas y las 3 pruebas terminaron con `OK`.

## Evidencia del ciclo TDD

El estado actual del código y el resultado exitoso prueban la etapa verde, pero no demuestran por sí solos que las pruebas se escribieron antes de la implementación. Para presentar evidencia completa del ciclo solicitado, adjuntar capturas o un registro real de estos momentos:

1. **Prueba inicial (rojo):** ejecutar las pruebas antes de implementar la regla y conservar la salida que muestra el fallo esperado.
2. **Implementación (verde):** implementar la comprobación de disponibilidad y ejecutar nuevamente las pruebas hasta obtener `OK`.
3. **Refactorización:** mostrar la separación entre la validación de datos en `ReservaForm.clean()` y la consulta de disponibilidad en `Cancha.esta_disponible()`, y volver a ejecutar las pruebas para confirmar que siguen pasando.

No se afirma aquí que la etapa roja se haya registrado históricamente: debe adjuntarse evidencia obtenida durante el proceso real, sin reconstruir ni alterar salidas de consola.
