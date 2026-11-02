# Decisiones · HU-10 Solicitar vacaciones

## 1. ¿Qué pasos son workflow y cuáles son agente? ¿Por qué?
La orquestación general es un workflow determinista implementado con LangGraph/StateGraph: filtro de seguridad, criterios, casos, aprobación, construcción, verificación, despliegue, automatización, E2E, triage y reporte siguen transiciones definidas en código. Dentro de ese workflow hay agentes que razonan y producen resultados, como analista, desarrollador, automatizador, despliegue y triage. El workflow controla el proceso; los agentes resuelven las tareas que requieren razonamiento.

## 2. ¿Cómo se validó cada salida estructurada, de los criterios al código? ¿Qué atrapó algún validador?
El flujo generó 11 escenarios en criterios.feature y 20 casos en casos_prueba.json antes de construir la aplicación. Después de aprobar el plan se ejecutaron verificaciones, despliegue y pruebas automatizadas. Las pruebas E2E detectaron inicialmente una falla: la validación de antigüedad impedía llegar a la regla de días disponibles. Después de la corrección, una segunda ejecución todavía tuvo una falla y el triage identificó que el problema restante estaba en el test. La ejecución final terminó con 34 passed y 4 skipped.

## 3. ¿Dónde intervine como persona y qué vi para decidir?
Intervine en los checkpoints HITL. Después del análisis acepté continuar aun cuando el analista reportó preguntas abiertas, porque las convenciones ya establecían el comportamiento 422 de FastAPI para payloads inválidos y el modelo ya contenía fecha_ingreso. Después revisé el primer plan del desarrollador y lo aprobé porque contemplaba modelo, reglas de antigüedad, festivos, días hábiles, orden de validaciones, endpoints y data-testid requeridos.

## 4. ¿Qué arquitectura de orquestación usa mi fábrica y por qué no otra de las que vimos?
La fábrica usa un supervisor determinista escrito en código mediante LangGraph/StateGraph. Las transiciones y ciclos están definidos por el grafo y el triage enruta el fallo al responsable. Es apropiado para este reto porque el proceso y sus controles deben ser reproducibles y auditables; no se necesita que los agentes decidan libremente quién ejecuta el siguiente paso como ocurriría en una topología de red o de handoffs.

## 5. Si algo falló: ¿qué corregí en el agente y por qué no en su resultado?
Hubo dos ciclos de corrección. Primero, el triage envió el problema al desarrollador por una validación incorrecta de antigüedad; el agente corrigió el código y se redesplegó. En el segundo ciclo, el triage determinó que el fallo restante correspondía al automatizador porque el test esperaba un resultado contrario al criterio de aceptación. El automatizador corrigió la prueba. No edité manualmente los archivos generados de app/ ni salida/: las correcciones fueron enrutadas al agente responsable. El resultado final fue 34 passed, 4 skipped y 0 failed.
