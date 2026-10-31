"""Pruebas de API para HU-03: editar y dar de baja a un empleado.

Nota sobre el diseño: igual que en tests/api/test_hu_02.py, la base de
datos es compartida y persistente entre ejecuciones, y numero_empleado se
asigna de forma secuencial. Por eso cada prueba crea su propio empleado
(correo único vía uuid) y usa el numero_empleado devuelto por la API en
vez de asumir valores fijos como EMP-0001.
"""
import uuid
from datetime import date, timedelta

import httpx


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


def _dar_de_baja(client: httpx.Client, numero_empleado: str, fecha_baja: str) -> dict:
    respuesta = client.put(
        f"/api/empleados/{numero_empleado}/baja", json={"fecha_baja": fecha_baja}
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def test_cp01_editar_puesto_y_departamento_de_empleado_activo(url_api):
    """CP-01: Editar puesto y departamento de un empleado activo."""
    tag = _etiqueta()
    with httpx.Client(base_url=url_api) as client:
        empleado = _crear_empleado(client, f"Carla Díaz {tag}", "Analista", "Ventas")
        numero = empleado["numero_empleado"]

        respuesta = client.put(
            f"/api/empleados/{numero}",
            json={"puesto": "Analista Senior", "departamento": "Finanzas"},
        )
        assert respuesta.status_code == 200, respuesta.text

        consulta = client.get(f"/api/empleados/{numero}")

    assert consulta.status_code == 200
    datos = consulta.json()
    assert datos["puesto"] == "Analista Senior"
    assert datos["departamento"] == "Finanzas"
    assert datos["estado"] == "activo"


def test_cp03_numero_empleado_y_correo_no_se_modifican(url_api):
    """CP-03: El número de empleado y el correo no se modifican al editar."""
    tag = _etiqueta()
    with httpx.Client(base_url=url_api) as client:
        empleado = _crear_empleado(client, f"Ana López {tag}", "Analista", "Ventas")
        numero = empleado["numero_empleado"]
        correo_original = empleado["correo"]

        respuesta = client.put(
            f"/api/empleados/{numero}",
            json={
                "numero_empleado": "EMP-9999",
                "correo": "otro@empresa.com",
                "puesto": "Analista",
                "departamento": "Operaciones",
            },
        )
        assert respuesta.status_code == 200, respuesta.text

        consulta = client.get(f"/api/empleados/{numero}")

    assert consulta.status_code == 200
    datos = consulta.json()
    assert datos["numero_empleado"] == numero
    assert datos["correo"] == correo_original


def test_cp05_rechazar_edicion_con_puesto_invalido(url_api):
    """CP-05: Rechazar la edición con un puesto inválido."""
    tag = _etiqueta()
    with httpx.Client(base_url=url_api) as client:
        empleado = _crear_empleado(client, f"Jorge Ruiz {tag}", "Analista", "Tecnología")
        numero = empleado["numero_empleado"]

        respuesta = client.put(
            f"/api/empleados/{numero}",
            json={"puesto": "A", "departamento": "Tecnología"},
        )

    assert respuesta.status_code == 422
    assert "puesto" in respuesta.json()["detail"].lower()


def test_cp07_rechazar_edicion_con_departamento_invalido(url_api):
    """CP-07: Rechazar la edición con un departamento inválido."""
    tag = _etiqueta()
    with httpx.Client(base_url=url_api) as client:
        empleado = _crear_empleado(client, f"Iván Soto {tag}", "Analista", "Tecnología")
        numero = empleado["numero_empleado"]

        respuesta = client.put(
            f"/api/empleados/{numero}",
            json={"puesto": "Analista", "departamento": "Marketing"},
        )

    assert respuesta.status_code == 422
    assert "departamento" in respuesta.json()["detail"].lower()


def test_cp09_rechazar_edicion_de_empleado_dado_de_baja(url_api):
    """CP-09: Rechazar la edición de un empleado dado de baja."""
    tag = _etiqueta()
    with httpx.Client(base_url=url_api) as client:
        empleado = _crear_empleado(client, f"Sofía Torres {tag}", "Analista", "Finanzas")
        numero = empleado["numero_empleado"]
        _dar_de_baja(client, numero, date.today().isoformat())

        respuesta = client.put(
            f"/api/empleados/{numero}",
            json={"puesto": "Analista Senior", "departamento": "Finanzas"},
        )

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "No se puede editar a un empleado dado de baja"


def test_cp11_dar_de_baja_a_un_empleado_activo(url_api):
    """CP-11: Dar de baja a un empleado activo."""
    tag = _etiqueta()
    with httpx.Client(base_url=url_api) as client:
        empleado = _crear_empleado(client, f"Marco Vidal {tag}", "Analista", "Operaciones")
        numero = empleado["numero_empleado"]
        fecha_baja = date.today().isoformat()

        respuesta = client.put(
            f"/api/empleados/{numero}/baja", json={"fecha_baja": fecha_baja}
        )
        assert respuesta.status_code == 200, respuesta.text
        datos = respuesta.json()
        assert datos["estado"] == "baja"
        assert datos["fecha_baja"] == fecha_baja

        listado = client.get("/api/empleados", params={"buscar": tag})

    assert listado.status_code == 200
    assert any(e["numero_empleado"] == numero for e in listado.json())


def test_cp13_rechazar_baja_con_fecha_anterior_a_fecha_ingreso(url_api):
    """CP-13: Rechazar la baja con una fecha de baja anterior a la fecha de ingreso."""
    tag = _etiqueta()
    with httpx.Client(base_url=url_api) as client:
        empleado = _crear_empleado(client, f"Elena Ríos {tag}", "Analista", "Tecnología")
        numero = empleado["numero_empleado"]
        fecha_baja = (date.today() - timedelta(days=30)).isoformat()

        respuesta = client.put(
            f"/api/empleados/{numero}/baja", json={"fecha_baja": fecha_baja}
        )

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == (
        "La fecha de baja no puede ser anterior a la fecha de ingreso"
    )
