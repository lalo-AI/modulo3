"""Pruebas E2E para HU-02: consultar el directorio de empleados.

Nota sobre el diseño: ver el comentario de cabecera en
tests/api/test_hu_02.py. Las precondiciones se crean vía API (correos
únicos con uuid) y las verificaciones ubican filas por el número de
empleado capturado al crear, no por un id de fila fijo (fila-empleado-1,
numero-empleado-1, etc.), porque el id de base de datos depende del
historial acumulado y no es controlable por la prueba.
"""
import uuid
from datetime import date

import httpx
import pytest
from playwright.sync_api import expect


def _correo_unico() -> str:
    return f"empleado.{uuid.uuid4().hex[:12]}@empresa.com"


def _etiqueta() -> str:
    return uuid.uuid4().hex[:8]


def _crear_empleado(url_api: str, nombre: str, puesto: str, departamento: str) -> dict:
    payload = {
        "nombre": nombre,
        "correo": _correo_unico(),
        "puesto": puesto,
        "departamento": departamento,
        "fecha_ingreso": date.today().isoformat(),
    }
    respuesta = httpx.post(f"{url_api}/api/empleados", json=payload)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def test_cp04_buscar_por_nombre(page, url_api, url_web):
    """CP-04: Buscar un empleado por nombre."""
    tag = _etiqueta()
    ana = _crear_empleado(url_api, f"Ana Gómez {tag}", "Analista", "Tecnología")
    _crear_empleado(url_api, f"Luis Pérez {tag}", "Ejecutivo de ventas", "Ventas")

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(f"Ana Gómez {tag}")

    filas = page.locator('[data-testid^="fila-empleado-"]')
    expect(filas).to_have_count(1)
    numero = filas.locator('[data-testid^="numero-empleado-"]')
    expect(numero).to_have_text(ana["numero_empleado"])


def test_cp06_buscar_por_correo_sin_distinguir_mayusculas(page, url_api, url_web):
    """CP-06: Buscar un empleado por correo sin distinguir mayúsculas de minúsculas."""
    ana = _crear_empleado(url_api, f"Ana Gómez {_etiqueta()}", "Analista", "Tecnología")

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(ana["correo"].upper())

    filas = page.locator('[data-testid^="fila-empleado-"]')
    expect(filas).to_have_count(1)
    numero = filas.locator('[data-testid^="numero-empleado-"]')
    expect(numero).to_have_text(ana["numero_empleado"])


def test_cp08_filtrar_por_departamento(page, url_api, url_web):
    """CP-08: Filtrar empleados por departamento."""
    tag = _etiqueta()
    luis = _crear_empleado(url_api, f"Luis Pérez {tag}", "Ejecutivo de ventas", "Ventas")

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(tag)
    page.get_by_test_id("filtro-departamento").select_option("Ventas")

    filas = page.locator('[data-testid^="fila-empleado-"]')
    expect(filas).to_have_count(1)
    expect(filas).to_contain_text(luis["nombre"])
    expect(filas).to_contain_text("Ventas")


def test_cp10_buscar_sin_coincidencias(page, url_api, url_web):
    """CP-10: Buscar un texto que no coincide con ningún empleado."""
    _crear_empleado(url_api, f"Ana Gómez {_etiqueta()}", "Analista", "Tecnología")

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(f"Zzzxyz{_etiqueta()}")

    expect(page.locator('[data-testid^="fila-empleado-"]')).to_have_count(0)
    sin_resultados = page.get_by_test_id("sin-resultados")
    expect(sin_resultados).to_be_visible()
    expect(sin_resultados).to_have_text("No se encontraron empleados")


@pytest.mark.skip(
    reason=(
        "No existe endpoint ni acción en la UI para dar de baja a un "
        "empleado. Esa capacidad es de HU-03 (editar-dar-baja), aún no "
        "implementada; no se puede construir la precondición 'empleado con "
        "estado baja'."
    )
)
def test_cp02_ver_directorio_completo(page, url_api, url_web):
    """CP-02: Ver el directorio completo de empleados."""


@pytest.mark.skip(
    reason=(
        "No existe endpoint ni acción en la UI para dar de baja a un "
        "empleado. Esa capacidad es de HU-03 (editar-dar-baja), aún no "
        "implementada; no se puede construir la precondición 'empleado con "
        "estado baja'."
    )
)
def test_cp12_empleado_baja_sigue_en_directorio(page, url_api, url_web):
    """CP-12: Un empleado dado de baja sigue apareciendo en el directorio."""
