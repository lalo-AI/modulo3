"""Pruebas de API para HU-10: solicitar vacaciones.

Nota sobre el diseño: igual que en tests/api/test_hu_03.py, la base de
datos es compartida y persistente entre ejecuciones y el `id` numérico
de un empleado (el que usa /api/empleados/{empleado_id}/vacaciones) se
asigna de forma secuencial. Por eso cada prueba crea su propio empleado
(correo único vía uuid) con la fecha_ingreso que necesita el caso, y usa
el `id` devuelto por la API en vez de asumir valores fijos como 7, 8 o 9.
"""
import uuid

import httpx


def _correo_unico() -> str:
    return f"empleado.{uuid.uuid4().hex[:12]}@empresa.com"


def _etiqueta() -> str:
    return uuid.uuid4().hex[:8]


def _crear_empleado(
    client: httpx.Client, nombre: str, fecha_ingreso: str, departamento: str = "Tecnología"
) -> dict:
    payload = {
        "nombre": nombre,
        "correo": _correo_unico(),
        "puesto": "Analista",
        "departamento": departamento,
        "fecha_ingreso": fecha_ingreso,
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


def _solicitar_vacaciones(
    client: httpx.Client, empleado_id: int, fecha_inicio: str, fecha_fin: str
) -> httpx.Response:
    return client.post(
        f"/api/empleados/{empleado_id}/vacaciones",
        json={"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin},
    )


def test_cp01_registra_una_solicitud_valida(url_api):
    """CP-01: Camino feliz - se registra una solicitud válida."""
    tag = _etiqueta()
    with httpx.Client(base_url=url_api) as client:
        empleado = _crear_empleado(client, f"Ana Torres {tag}", "2025-01-10")

        respuesta = _solicitar_vacaciones(client, empleado["id"], "2026-12-21", "2026-12-31")

    assert respuesta.status_code == 201, respuesta.text
    datos = respuesta.json()
    assert datos["dias_habiles"] == 8
    assert datos["dias_restantes"] == 4


def test_cp03_festivos_y_fin_de_semana_no_se_descuentan(url_api):
    """CP-03: Los sábados, domingos y festivos dentro del periodo no se descuentan."""
    tag = _etiqueta()
    with httpx.Client(base_url=url_api) as client:
        empleado = _crear_empleado(client, f"Ana Torres {tag}", "2025-01-10")

        respuesta = _solicitar_vacaciones(client, empleado["id"], "2026-09-14", "2026-09-18")

    assert respuesta.status_code == 201, respuesta.text
    assert respuesta.json()["dias_habiles"] == 4


def test_cp04_acepta_solicitud_que_usa_exactamente_los_dias_que_quedan(url_api):
    """CP-04: Se acepta una solicitud que usa exactamente los días que quedan en el año."""
    tag = _etiqueta()
    with httpx.Client(base_url=url_api) as client:
        empleado = _crear_empleado(client, f"Ana Torres {tag}", "2025-01-10")
        previa = _solicitar_vacaciones(client, empleado["id"], "2026-07-06", "2026-07-10")
        assert previa.status_code == 201, previa.text
        assert previa.json()["dias_habiles"] == 5

        respuesta = _solicitar_vacaciones(client, empleado["id"], "2026-07-13", "2026-07-21")

    assert respuesta.status_code == 201, respuesta.text
    datos = respuesta.json()
    assert datos["dias_habiles"] == 7
    assert datos["dias_restantes"] == 0


def test_cp05_rechaza_empleado_inexistente(url_api):
    """CP-05: Error - el empleado no existe."""
    with httpx.Client(base_url=url_api) as client:
        respuesta = _solicitar_vacaciones(client, 999999999, "2026-07-06", "2026-07-10")

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Empleado no encontrado"


def test_cp06_rechaza_empleado_dado_de_baja(url_api):
    """CP-06: Error - el empleado está dado de baja."""
    tag = _etiqueta()
    with httpx.Client(base_url=url_api) as client:
        empleado = _crear_empleado(client, f"María López {tag}", "2023-01-05")
        _dar_de_baja(client, empleado["numero_empleado"], "2026-01-02")

        respuesta = _solicitar_vacaciones(client, empleado["id"], "2026-07-06", "2026-07-10")

    assert respuesta.status_code == 409
    assert (
        respuesta.json()["detail"]
        == "No se pueden solicitar vacaciones para un empleado dado de baja"
    )


def test_cp07_rechaza_fecha_fin_anterior_a_fecha_inicio(url_api):
    """CP-07: Error - la fecha de fin es anterior a la fecha de inicio."""
    tag = _etiqueta()
    with httpx.Client(base_url=url_api) as client:
        empleado = _crear_empleado(client, f"Ana Torres {tag}", "2025-01-10")

        respuesta = _solicitar_vacaciones(client, empleado["id"], "2026-07-10", "2026-07-05")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La fecha de fin no puede ser anterior a la fecha de inicio"
    )


def test_cp08_rechaza_periodo_que_cruza_de_un_anio_a_otro(url_api):
    """CP-08: Error - el periodo cruza de un año a otro."""
    tag = _etiqueta()
    with httpx.Client(base_url=url_api) as client:
        empleado = _crear_empleado(client, f"Ana Torres {tag}", "2025-01-10")

        respuesta = _solicitar_vacaciones(client, empleado["id"], "2026-12-28", "2027-01-08")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "Las vacaciones deben estar dentro de un mismo año calendario"
    )


def test_cp09_rechaza_anio_no_soportado(url_api):
    """CP-09: Error - el año de la solicitud no está soportado."""
    tag = _etiqueta()
    with httpx.Client(base_url=url_api) as client:
        empleado = _crear_empleado(client, f"Ana Torres {tag}", "2025-01-10")

        respuesta = _solicitar_vacaciones(client, empleado["id"], "2025-07-01", "2025-07-05")

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "Solo se pueden solicitar vacaciones en 2026 y 2027"


def test_cp10_rechaza_antiguedad_insuficiente(url_api):
    """CP-10: Error - antigüedad insuficiente."""
    tag = _etiqueta()
    with httpx.Client(base_url=url_api) as client:
        empleado = _crear_empleado(client, f"Luis Pérez {tag}", "2025-12-21")

        respuesta = _solicitar_vacaciones(client, empleado["id"], "2026-12-18", "2026-12-18")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "Se requiere al menos un año de antigüedad a la fecha de inicio"
    )


def test_cp11_rechaza_periodo_sin_dias_habiles(url_api):
    """CP-11: Error - el periodo no tiene ningún día hábil."""
    tag = _etiqueta()
    with httpx.Client(base_url=url_api) as client:
        empleado = _crear_empleado(client, f"Ana Torres {tag}", "2025-01-10")

        respuesta = _solicitar_vacaciones(client, empleado["id"], "2026-07-11", "2026-07-12")

    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "El periodo no incluye días hábiles"


def test_cp12_rechaza_solicitud_que_excede_los_dias_disponibles(url_api):
    """CP-12: Error - la solicitud excede los días disponibles del año."""
    tag = _etiqueta()
    with httpx.Client(base_url=url_api) as client:
        empleado = _crear_empleado(client, f"Ana Torres {tag}", "2025-01-10")
        previa = _solicitar_vacaciones(client, empleado["id"], "2026-01-12", "2026-01-15")
        assert previa.status_code == 201, previa.text
        assert previa.json()["dias_habiles"] == 4

        respuesta = _solicitar_vacaciones(client, empleado["id"], "2026-02-09", "2026-02-19")

    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La solicitud excede los días disponibles: quedan 8 días hábiles"
    )
