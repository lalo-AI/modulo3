# language: es
# Historia relacionada: historias/HU-02-consultar-directorio.md

Característica: Consultar el directorio de empleados
  Como persona del área de Recursos Humanos
  Quiero ver el directorio de empleados, buscarlos por nombre o correo y filtrarlos por departamento
  Para encontrar rápido a una persona

  Escenario: Ver el directorio completo de empleados
    Dado que existen los siguientes empleados registrados:
      | numero_empleado | nombre        | puesto          | departamento        | estado |
      | EMP-0001        | Ana Gómez     | Analista        | Tecnología          | activo |
      | EMP-0002        | Luis Pérez    | Vendedor        | Ventas              | activo |
      | EMP-0003        | Marta Ruiz    | Contadora       | Finanzas            | baja   |
    Cuando la persona de Recursos Humanos abre el directorio de empleados
    Entonces ve una lista con 3 empleados
    Y cada fila muestra número de empleado, nombre, puesto, departamento y estado

  Escenario: Buscar un empleado por nombre
    Dado que existen los siguientes empleados registrados:
      | numero_empleado | nombre        | puesto          | departamento        | estado |
      | EMP-0001        | Ana Gómez     | Analista        | Tecnología          | activo |
      | EMP-0002        | Luis Pérez    | Vendedor        | Ventas              | activo |
    Cuando busca en el directorio el texto "Ana"
    Entonces ve 1 resultado
    Y el resultado muestra a "Ana Gómez" con número "EMP-0001"

  Escenario: Buscar un empleado por correo sin distinguir mayúsculas de minúsculas
    Dado que existe el empleado "Ana Gómez" con correo "ana.gomez@empresa.com" y número "EMP-0001"
    Cuando busca en el directorio el texto "ANA.GOMEZ@EMPRESA.COM"
    Entonces ve 1 resultado
    Y el resultado muestra a "Ana Gómez" con número "EMP-0001"

  Escenario: Filtrar empleados por departamento
    Dado que existen los siguientes empleados registrados:
      | numero_empleado | nombre        | puesto          | departamento        | estado |
      | EMP-0001        | Ana Gómez     | Analista        | Tecnología          | activo |
      | EMP-0002        | Luis Pérez    | Vendedor        | Ventas              | activo |
      | EMP-0003        | Marta Ruiz    | Contadora       | Finanzas            | activo |
    Cuando filtra el directorio por el departamento "Ventas"
    Entonces ve 1 resultado
    Y el resultado muestra a "Luis Pérez" con departamento "Ventas"

  Escenario: Buscar un texto que no coincide con ningún empleado
    Dado que existen los siguientes empleados registrados:
      | numero_empleado | nombre        | puesto          | departamento        | estado |
      | EMP-0001        | Ana Gómez     | Analista        | Tecnología          | activo |
      | EMP-0002        | Luis Pérez    | Vendedor        | Ventas              | activo |
    Cuando busca en el directorio el texto "Zzzxyz"
    Entonces ve 0 resultados
    Y ve el mensaje "No se encontraron empleados"

  Escenario: Un empleado dado de baja sigue apareciendo en el directorio
    Dado que existe el empleado "Marta Ruiz" con número "EMP-0003", estado "baja" y fecha de baja "2024-03-01"
    Cuando la persona de Recursos Humanos abre el directorio de empleados
    Entonces ve a "Marta Ruiz" en la lista
    Y el estado mostrado para "EMP-0003" es "baja"

# Preguntas abiertas
# - No se especifica si la búsqueda es por coincidencia parcial o exacta del nombre/correo; se asumió coincidencia parcial.
# - No se indica si el directorio pagina resultados cuando hay muchos empleados.
# - No se especifica si se pueden combinar búsqueda por texto y filtro por departamento al mismo tiempo.
