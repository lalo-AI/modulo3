# Reporte · HU-03

**Estado:** LISTA
**Costo de agentes:** 2.33 USD
**Ciclos de corrección:** 2

## Bitácora
- Filtro de historia: OK
- Criterios escritos en criterios.feature
- Preguntas abiertas: la persona respondió 'si'
- Casos de prueba escritos en casos_prueba.json
- Plan aprobado por una persona
- Construcción 1
- Verificación: OK
- Pruebas automatizadas: OK (14 casos)
- Despliegue: OK
- Despliegue y pruebas listos
- Pruebas E2E: 6 failed, 17 passed, 3 skipped in 37.75s
- Triage → automatizador: El selector get_by_test_id("empleado-puesto") no es único: existe tanto en el formulario de alta/registro (que queda montado en la misma página) como en el formulario de edición, provocando "strict mode violation" al resolver dos elementos. Además, en el caso de EMP-0025 la prueba intenta hacer click en el botón "Editar" cuando éste aparece deshabilitado (comportamiento esperado para un empleado dado de baja, según el escenario "Rechazar la edición de un empleado dado de baja"), y en el caso de dar de baja a un empleado activo la prueba busca "mensaje-exito" sin haber esperado a que la navegación/acción de alta se completara o sin haber ubicado el formulario correcto, mezclando el flujo de "Registrar empleado" con el de "editar/dar de baja".
- Pruebas corregidas
- Pruebas E2E: 3 failed, 19 passed, 4 skipped in 17.26s
- Triage → desarrollador: Al intentar editar o dar de baja a un empleado, la aplicación no navega a la pantalla/estado esperado tras la acción, sino que se queda (o redirige) en la pantalla "Registrar empleado". Por eso no aparece el elemento con test-id "mensaje-exito" tras las acciones de editar (CP02, CP04) y dar de baja (CP12), lo que indica que el flujo de edición/baja no está implementado o enlazado correctamente en la aplicación, mostrando el formulario de alta en vez de confirmar la operación.
- Código corregido; redespliegue OK
- Pruebas E2E: 22 passed, 4 skipped in 2.79s

## Última ejecución de pruebas
```
22 passed, 4 skipped in 2.79s

```