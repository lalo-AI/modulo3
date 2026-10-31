# language: es
# Historia: HU-03 · Editar y dar de baja a un empleado

Característica: Editar y dar de baja a un empleado
  Como persona del área de Recursos Humanos
  quiero cambiar el puesto y el departamento de un empleado, y poder darlo de baja
  para mantener el directorio al día sin perder el historial

  Escenario: Editar puesto y departamento de un empleado activo
    Dado que existe el empleado "EMP-0001" con puesto "Analista" y departamento "Ventas", en estado "activo"
    Cuando edito al empleado "EMP-0001" con puesto "Analista Senior" y departamento "Finanzas"
    Entonces la respuesta tiene código 200
    Y el empleado "EMP-0001" tiene puesto "Analista Senior" y departamento "Finanzas"
    Y el estado del empleado "EMP-0001" sigue siendo "activo"

  Escenario: El número de empleado y el correo no se modifican al editar
    Dado que existe el empleado "EMP-0002" con correo "ana.lopez@empresa.com", en estado "activo"
    Cuando edito al empleado "EMP-0002" enviando numero_empleado "EMP-9999" y correo "otro@empresa.com", junto con puesto "Analista" y departamento "Operaciones"
    Entonces la respuesta tiene código 200
    Y el empleado "EMP-0002" conserva el numero_empleado "EMP-0002"
    Y el empleado "EMP-0002" conserva el correo "ana.lopez@empresa.com"

  Escenario: Rechazar la edición con un puesto inválido
    Dado que existe el empleado "EMP-0003" con puesto "Analista", en estado "activo"
    Cuando edito al empleado "EMP-0003" con puesto "A" y departamento "Tecnología"
    Entonces la respuesta tiene código 422
    Y la pantalla muestra que el campo "puesto" debe corregirse

  Escenario: Rechazar la edición con un departamento inválido
    Dado que existe el empleado "EMP-0004" con departamento "Tecnología", en estado "activo"
    Cuando edito al empleado "EMP-0004" con puesto "Analista" y departamento "Marketing"
    Entonces la respuesta tiene código 422
    Y la pantalla muestra que el campo "departamento" debe corregirse

  Escenario: Rechazar la edición de un empleado dado de baja
    Dado que existe el empleado "EMP-0005" en estado "baja" con fecha_baja "2024-03-01"
    Cuando edito al empleado "EMP-0005" con puesto "Analista Senior" y departamento "Finanzas"
    Entonces la respuesta tiene código 409
    Y la respuesta contiene el mensaje "No se puede editar a un empleado dado de baja"

  Escenario: Dar de baja a un empleado activo
    Dado que existe el empleado "EMP-0006" con fecha_ingreso "2022-01-10", en estado "activo"
    Cuando doy de baja al empleado "EMP-0006" con fecha_baja "2024-05-15"
    Entonces la respuesta tiene código 200
    Y el estado del empleado "EMP-0006" es "baja"
    Y el empleado "EMP-0006" tiene fecha_baja "2024-05-15"
    Y el empleado "EMP-0006" sigue apareciendo en el directorio

  Escenario: Rechazar la baja con una fecha de baja anterior a la fecha de ingreso
    Dado que existe el empleado "EMP-0007" con fecha_ingreso "2023-06-01", en estado "activo"
    Cuando doy de baja al empleado "EMP-0007" con fecha_baja "2023-01-01"
    Entonces la respuesta tiene código 422
    Y la pantalla muestra que el campo "fecha_baja" debe corregirse

# Preguntas abiertas
# - ¿Qué sucede si se intenta dar de baja a un empleado que ya está en estado "baja"? La regla 6 solo menciona la edición, no queda claro si "dar de baja" cuenta como edición para ese caso.
# - ¿El nombre y la fecha de ingreso también se pueden editar en esta historia, o la edición se limita estrictamente a puesto y departamento como indica el enunciado?
