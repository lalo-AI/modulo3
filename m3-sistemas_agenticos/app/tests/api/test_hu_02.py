"""Pruebas de API para HU-02: consultar el directorio de empleados.

Nota sobre el diseño: la API asigna numero_empleado e id de forma secuencial
sobre una base de datos compartida y persistente entre ejecuciones. Para que
cada prueba pueda repetirse sin colisionar con datos de otras corridas
(correos únicos vía uuid), las búsquedas se acotan con una etiqueta única por
prueba en vez de asumir que la base está vacía o que los números de empleado
son EMP-0001/0002/0003. Los valores de numero_empleado y nombre se comparan
contra lo que la propia prueba creó, capturado de la respuesta de creación.
"""
import uuid
from datetime import date

import httpx
import pytest


def _correo_unico() -> str:
    return f"empleado.{uuid.uuid4().hex[:12]}@empresa.com"


def _etiqueta() -> str:
    return uuid.uuid4().hex[:8]


def _crear_empleado(client: httpx.Client, nombre: str, puesto: str, departamento: str) -> dict:
    payload = {
        "nombre": nombre,
        "correo": _correo_unico(),
        "puesto": puesto,
        "departamento": departamento,
        "fecha_ingreso": date.today().isoformat(),
    }
    respuesta = client.post("/api/empleados", json=payload)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def test_cp01_ver_directorio_completo(url_api):
    """CP-01: Ver el directorio completo de empleados."""
    tag = _etiqueta()
    with httpx.Client(base_url=url_api) as client:
        creados = [
            _crear_empleado(client, f"Ana Gómez {tag}", "Analista", "Tecnología"),
            _crear_empleado(client, f"Luis Pérez {tag}", "Ejecutivo de ventas", "Ventas"),
            _crear_empleado(client, f"Marta Ruiz {tag}", "Contadora", "Finanzas"),
        ]

        respuesta = client.get("/api/empleados", params={"buscar": tag})

    assert respuesta.status_code == 200
    empleados = respuesta.json()
    assert len(empleados) == 3
    assert {e["numero_empleado"] for e in empleados} == {c["numero_empleado"] for c in creados}
    for empleado in empleados:
        for campo in ("numero_empleado", "nombre", "puesto", "departamento", "estado"):
            assert empleado.get(campo)


def test_cp03_buscar_por_nombre(url_api):
    """CP-03: Buscar un empleado por nombre."""
    tag = _etiqueta()
    with httpx.Client(base_url=url_api) as client:
        ana = _crear_empleado(client, f"Ana Gómez {tag}", "Analista", "Tecnología")
        _crear_empleado(client, f"Luis Pérez {tag}", "Ejecutivo de ventas", "Ventas")

        respuesta = client.get("/api/empleados", params={"buscar": f"Ana Gómez {tag}"})

    assert respuesta.status_code == 200
    resultados = respuesta.json()
    assert len(resultados) == 1
    assert resultados[0]["nombre"] == f"Ana Gómez {tag}"
    assert resultados[0]["numero_empleado"] == ana["numero_empleado"]


def test_cp05_buscar_por_correo_sin_distinguir_mayusculas(url_api):
    """CP-05: Buscar un empleado por correo sin distinguir mayúsculas de minúsculas."""
    with httpx.Client(base_url=url_api) as client:
        ana = _crear_empleado(client, f"Ana Gómez {_etiqueta()}", "Analista", "Tecnología")

        respuesta = client.get("/api/empleados", params={"buscar": ana["correo"].upper()})

    assert respuesta.status_code == 200
    resultados = respuesta.json()
    assert len(resultados) == 1
    assert resultados[0]["nombre"] == ana["nombre"]
    assert resultados[0]["numero_empleado"] == ana["numero_empleado"]


def test_cp07_filtrar_por_departamento(url_api):
    """CP-07: Filtrar empleados por departamento."""
    tag = _etiqueta()
    with httpx.Client(base_url=url_api) as client:
        luis = _crear_empleado(client, f"Luis Pérez {tag}", "Ejecutivo de ventas", "Ventas")

        respuesta = client.get(
            "/api/empleados", params={"departamento": "Ventas", "buscar": tag}
        )

    assert respuesta.status_code == 200
    resultados = respuesta.json()
    assert len(resultados) == 1
    assert resultados[0]["nombre"] == luis["nombre"]
    assert resultados[0]["departamento"] == "Ventas"


def test_cp09_buscar_sin_coincidencias(url_api):
    """CP-09: Buscar un texto que no coincide con ningún empleado."""
    with httpx.Client(base_url=url_api) as client:
        _crear_empleado(client, f"Ana Gómez {_etiqueta()}", "Analista", "Tecnología")

        respuesta = client.get(
            "/api/empleados", params={"buscar": f"Zzzxyz{_etiqueta()}"}
        )

    assert respuesta.status_code == 200
    assert respuesta.json() == []


@pytest.mark.skip(
    reason=(
        "No existe endpoint para dar de baja a un empleado (POST "
        "/api/empleados siempre crea con estado 'activo' y no hay "
        "PATCH/PUT). Esa capacidad es de HU-03 (editar-dar-baja), aún no "
        "implementada; no se puede construir la precondición 'empleado con "
        "estado baja' desde fuera de la base de datos."
    )
)
def test_cp11_empleado_baja_sigue_en_directorio(url_api):
    """CP-11: Un empleado dado de baja sigue apareciendo en el directorio."""
