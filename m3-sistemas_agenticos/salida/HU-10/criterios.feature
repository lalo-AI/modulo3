# language: es

Característica: Solicitar vacaciones
  Como empleado de la empresa
  Quiero solicitar días de vacaciones indicando una fecha de inicio y una de fin
  Para que mi solicitud quede registrada y sepa cuántos días me quedan en el año

  Escenario: Camino feliz - se registra una solicitud válida
    Dado que el empleado "Ana Torres" existe, está activo y tiene fecha_ingreso "2025-01-10"
    Y que no tiene ninguna solicitud de vacaciones registrada en el año 2026
    Cuando solicita vacaciones con fecha_inicio "2026-12-21" y fecha_fin "2026-12-31"
    Entonces la API responde 201
    Y el campo "dias_habiles" de la respuesta es 8
    Y el campo "dias_restantes" de la respuesta es 4
    Y en la pantalla el elemento "vacaciones-mensaje" muestra "Solicitud registrada: 8 días hábiles. Te quedan 4 días hábiles en 2026."

  Escenario: Los sábados, domingos y festivos dentro del periodo no se descuentan
    Dado que el empleado "Ana Torres" existe, está activo y tiene fecha_ingreso "2025-01-10"
    Y que no tiene ninguna solicitud de vacaciones registrada en el año 2026
    Cuando solicita vacaciones con fecha_inicio "2026-09-14" y fecha_fin "2026-09-18"
    Entonces la API responde 201
    Y el campo "dias_habiles" de la respuesta es 4
    Y el 16 de septiembre de 2026, que es festivo oficial, no se cuenta como día hábil
    Y el 19 y 20 de septiembre de 2026, que son sábado y domingo, no se cuentan dentro del periodo

  Escenario: Se acepta una solicitud que usa exactamente los días que quedan en el año
    Dado que el empleado "Ana Torres" existe, está activo y tiene fecha_ingreso "2025-01-10"
    Y que ya tiene registrada una solicitud del "2026-07-06" al "2026-07-10" que consumió 5 días hábiles
    Cuando solicita vacaciones con fecha_inicio "2026-07-13" y fecha_fin "2026-07-21"
    Entonces la API responde 201
    Y el campo "dias_habiles" de la respuesta es 7
    Y el campo "dias_restantes" de la respuesta es 0

  Escenario: Error - el empleado no existe
    Dado que no existe ningún empleado con id 9999
    Cuando solicita vacaciones para el empleado 9999 con fecha_inicio "2026-07-06" y fecha_fin "2026-07-10"
    Entonces la API responde 404
    Y el campo "detail" de la respuesta es "Empleado no encontrado"

  Escenario: Error - el empleado está dado de baja
    Dado que el empleado "María López" existe, tiene fecha_ingreso "2023-01-05" y está en estado "baja"
    Cuando solicita vacaciones con fecha_inicio "2026-07-06" y fecha_fin "2026-07-10"
    Entonces la API responde 409
    Y el campo "detail" de la respuesta es "No se pueden solicitar vacaciones para un empleado dado de baja"

  Escenario: Error - la fecha de fin es anterior a la fecha de inicio
    Dado que el empleado "Ana Torres" existe, está activo y tiene fecha_ingreso "2025-01-10"
    Cuando solicita vacaciones con fecha_inicio "2026-07-10" y fecha_fin "2026-07-05"
    Entonces la API responde 400
    Y el campo "detail" de la respuesta es "La fecha de fin no puede ser anterior a la fecha de inicio"

  Escenario: Error - el periodo cruza de un año a otro
    Dado que el empleado "Ana Torres" existe, está activo y tiene fecha_ingreso "2025-01-10"
    Cuando solicita vacaciones con fecha_inicio "2026-12-28" y fecha_fin "2027-01-08"
    Entonces la API responde 400
    Y el campo "detail" de la respuesta es "Las vacaciones deben estar dentro de un mismo año calendario"

  Escenario: Error - el año de la solicitud no está soportado
    Dado que el empleado "Ana Torres" existe, está activo y tiene fecha_ingreso "2025-01-10"
    Cuando solicita vacaciones con fecha_inicio "2025-07-01" y fecha_fin "2025-07-05"
    Entonces la API responde 400
    Y el campo "detail" de la respuesta es "Solo se pueden solicitar vacaciones en 2026 y 2027"

  Escenario: Error - antigüedad insuficiente
    Dado que el empleado "Luis Pérez" existe, está activo y tiene fecha_ingreso "2025-12-21"
    Cuando solicita vacaciones con fecha_inicio "2026-12-18" y fecha_fin "2026-12-18"
    Entonces la API responde 400
    Y el campo "detail" de la respuesta es "Se requiere al menos un año de antigüedad a la fecha de inicio"

  Escenario: Error - el periodo no tiene ningún día hábil
    Dado que el empleado "Ana Torres" existe, está activo y tiene fecha_ingreso "2025-01-10"
    Cuando solicita vacaciones con fecha_inicio "2026-07-11" y fecha_fin "2026-07-12"
    Entonces la API responde 400
    Y el campo "detail" de la respuesta es "El periodo no incluye días hábiles"

  Escenario: Error - la solicitud excede los días disponibles del año
    Dado que el empleado "Ana Torres" existe, está activo y tiene fecha_ingreso "2025-01-10"
    Y que ya tiene registrada una solicitud del "2026-01-05" al "2026-01-08" que consumió 4 días hábiles
    Cuando solicita vacaciones con fecha_inicio "2026-02-09" y fecha_fin "2026-02-19"
    Entonces la API responde 400
    Y el campo "detail" de la respuesta es "La solicitud excede los días disponibles: quedan 8 días hábiles"

# Preguntas abiertas
# - No se especifica qué debe responder la API si `fecha_inicio` o `fecha_fin` vienen vacíos o ausentes
#   en el cuerpo de la solicitud (se asume el 422 automático de FastAPI por payload inválido, igual que
#   un formato de fecha incorrecto, pero no hay un mensaje de `detail` confirmado para ese caso).
# - No se especifica qué debe responder la API si falta `fecha_ingreso` en un empleado creado antes de
#   esta historia (HU-01 a HU-03) y aún no se le ha migrado ese dato.
