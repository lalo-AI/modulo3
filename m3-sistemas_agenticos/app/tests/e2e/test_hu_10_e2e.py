"""Pruebas E2E para HU-10: solicitar vacaciones.

Nota sobre el diseño: ver el comentario de cabecera en
tests/api/test_hu_10.py. El botón que abre el formulario
(data-testid=vacaciones-abrir-{empleado_id}) usa el `id` numérico del
empleado, así que la precondición se crea vía API y la prueba localiza
el botón con el `id` devuelto en vez de asumir un valor fijo como 7.
"""
import uuid

import httpx
from playwright.sync_api import expect


def _correo_unico() -> str:
    return f"empleado.{uuid.uuid4().hex[:12]}@empresa.com"


def _etiqueta() -> str:
    return uuid.uuid4().hex[:8]


def _crear_empleado(url_api: str, nombre: str, fecha_ingreso: str) -> dict:
    payload = {
        "nombre": nombre,
        "correo": _correo_unico(),
        "puesto": "Analista",
        "departamento": "Tecnología",
        "fecha_ingreso": fecha_ingreso,
    }
    respuesta = httpx.post(f"{url_api}/api/empleados", json=payload)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def test_cp02_registra_una_solicitud_valida(page, url_api, url_web):
    """CP-02: Camino feliz - se registra una solicitud válida."""
    tag = _etiqueta()
    empleado = _crear_empleado(url_api, f"Ana Torres {tag}", "2025-01-10")
    numero = empleado["numero_empleado"]
    empleado_id = empleado["id"]

    page.goto(url_web)
    expect(page.get_by_test_id(f"fila-empleado-{numero}")).to_be_visible()
    page.get_by_test_id(f"vacaciones-abrir-{empleado_id}").click()
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-12-21")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-12-31")
    page.get_by_test_id("vacaciones-enviar").click()

    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Solicitud registrada: 8 días hábiles. Te quedan 4 días hábiles en 2026."
    )
