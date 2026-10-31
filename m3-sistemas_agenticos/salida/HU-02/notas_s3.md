# Lab 3 - Notas de ejecución HU-02

## Despliegue Docker

La aplicación fue desplegada correctamente mediante Docker Compose.

Resultado de `docker compose ps`:

- backend: Up / healthy
- backend puerto: 8000
- frontend: Up
- frontend puerto: 8080

La aplicación fue validada manualmente en:

http://localhost:8080

El directorio de empleados correspondiente a HU-02 se mostró correctamente.

## Ejecución paralela

Después de que la aplicación fue verificada, el flujo ejecutó en paralelo los agentes:

- despliegue
- automatizador

Ambos procesos finalizaron correctamente:

- Despliegue: OK
- Pruebas automatizadas: OK (12 casos)
- Despliegue y pruebas listos

Costo total reportado por el flujo HU-02: USD 1.13.

## Pruebas automatizadas

Resultado combinado:

    uv run python -m pytest tests -q -rs

Resultado:

    9 passed, 3 skipped in 3.33s

Los tres casos omitidos requieren la capacidad de dar de baja a un empleado. Esa funcionalidad corresponde a HU-03 y todavía no está implementada.

Pruebas API:

    5 passed, 1 skipped

Pruebas E2E:

    4 passed, 2 skipped

No se presentaron pruebas fallidas.

## Comparación con las pruebas manuales de HU-01

En HU-01 se realizaron manualmente cinco validaciones principales sobre el registro de empleados.

En HU-02 el agente automatizador generó 12 casos distribuidos entre pruebas API y E2E. La automatización permite ejecutar las validaciones de forma repetible y detectar regresiones sin sustituir las validaciones de negocio realizadas previamente sobre HU-01.

## Auditoría y control por roles

Conteo registrado en auditoria.jsonl:

- desarrollador: 53
- automatizador: 30
- despliegue: 24
- desarrollador-plan: 9

La seguridad de escritura se implementa mediante el hook `confinar_escritura`, que valida las rutas permitidas para cada rol antes de ejecutar Write/Edit. Cuando una operación no cumple las restricciones, `_denegar()` devuelve `permissionDecision: deny`.

Durante esta ejecución de HU-02 no se identificó en `auditoria.jsonl` un intento de escritura fuera de las rutas permitidas que pudiera documentarse como una denegación real. Por lo tanto, no se reporta una operación permitida como si hubiera sido denegada.

La única operación Edit identificada para el automatizador correspondió a:

    app/tests/api/test_hu_02.py

Esta operación está permitida para ese rol porque el automatizador tiene autorización de escritura sobre `tests/*`.

## Resultado

HU-02 completada correctamente.

- Aplicación: LISTA
- Verificación: OK
- Docker: OK
- Pruebas automatizadas: OK
- Ejecución paralela: OK
