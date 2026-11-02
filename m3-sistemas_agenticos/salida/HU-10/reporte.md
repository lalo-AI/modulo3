# Reporte · HU-10

**Estado:** LISTA
**Costo de agentes:** 1.86 USD
**Ciclos de corrección:** 2

## Bitácora
- Filtro de historia: OK
- Criterios escritos en criterios.feature
- Preguntas abiertas: la persona respondió 'si'
- Casos de prueba escritos en casos_prueba.json
- Plan aprobado por una persona
- Construcción 1
- Verificación: OK
- Pruebas automatizadas: OK (12 casos)
- Despliegue: OK
- Despliegue y pruebas listos
- Pruebas E2E: 1 failed, 33 passed, 4 skipped in 3.30s
- Triage → desarrollador: La API está devolviendo erróneamente "Se requiere al menos un año de antigüedad a la fecha de inicio" (400) para la prueba de "excede los días disponibles del año", en lugar de evaluar correctamente la antigüedad y el consumo de días. Según el criterio, Ana Torres tiene fecha_ingreso 2025-01-10, por lo que al 2026-02-09 ya cumple más de un año de antigüedad, y además ya tiene registrada una solicitud previa que consumió 4 días hábiles del año 2026. El sistema debería validar la antigüedad correctamente (pasando esa validación) y luego calcular que la nueva solicitud del 2026-02-09 al 2026-02-19 excede los 8 días hábiles restantes, devolviendo el detail "La solicitud excede los días disponibles: quedan 8 días hábiles" con status 400. El fallo indica que la lógica de validación de antigüedad se está aplicando incorrectamente (posiblemente usando mal la fecha de referencia o comparando mal fechas), bloqueando el flujo antes de llegar a la validación de días disponibles.
- Código corregido; redespliegue OK
- Pruebas E2E: 1 failed, 33 passed, 4 skipped in 3.50s
- Triage → automatizador: El test test_cp12_rechaza_solicitud_que_excede_los_dias_disponibles espera un 201, pero según el criterio de aceptación "Error - la solicitud excede los días disponibles del año" la API debe responder 400 con detail "La solicitud excede los días disponibles: quedan 8 días hábiles". Además, la respuesta 400 obtenida corresponde al mensaje de antigüedad insuficiente, lo que indica que el empleado configurado en el test no tiene una fecha_ingreso con al menos un año de antigüedad respecto a la fecha_inicio usada (2026-02-09), probablemente porque el test usa datos de setup distintos a los definidos en el escenario (fecha_ingreso "2025-01-10" para Ana Torres) o no configura correctamente al empleado/las solicitudes previas del escenario correspondiente.
- Pruebas corregidas
- Pruebas E2E: 34 passed, 4 skipped in 3.29s

## Última ejecución de pruebas
```
34 passed, 4 skipped in 3.29s

```