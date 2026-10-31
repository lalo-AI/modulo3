"""Pruebas E2E para HU-03: editar y dar de baja a un empleado.

Nota sobre el diseño: ver el comentario de cabecera en
tests/api/test_hu_03.py y en tests/e2e/test_hu_02_e2e.py. Las
precondiciones se crean vía API (correos únicos con uuid) y las
verificaciones ubican filas y controles por el numero_empleado devuelto
al crear, no por un id fijo como EMP-0001.
"""
import uuid
from datetime import date, timedelta

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


def _dar_de_baja(url_api: str, numero_empleado: str, fecha_baja: str) -> dict:
    respuesta = httpx.put(
        f"{url_api}/api/empleados/{numero_empleado}/baja", json={"fecha_baja": fecha_baja}
    )
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def _formulario_edicion(page, numero_empleado: str):
    """Acota el locator al <form> de edición: empleado-puesto y empleado-departamento
    también existen en el formulario de alta, siempre montado en la misma página."""
    return page.locator("form", has_text=f"Editar empleado {numero_empleado}")


def _formulario_baja(page, numero_empleado: str):
    return page.locator("form", has_text=f"Dar de baja a {numero_empleado}")


def test_cp02_editar_puesto_y_departamento_de_empleado_activo(page, url_api, url_web):
    """CP-02: Editar puesto y departamento de un empleado activo."""
    tag = _etiqueta()
    empleado = _crear_empleado(url_api, f"Carla Díaz {tag}", "Analista", "Ventas")
    numero = empleado["numero_empleado"]

    page.goto(url_web)
    expect(page.get_by_test_id(f"fila-empleado-{numero}")).to_be_visible()
    page.get_by_test_id(f"editar-empleado-{numero}").click()
    formulario = page.locator("form", has_text=f"Editar empleado {numero}")
    formulario.get_by_test_id("empleado-puesto").fill("Analista Senior")
    formulario.get_by_test_id("empleado-departamento").select_option("Finanzas")
    formulario.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("mensaje-exito")).to_be_visible()
    fila = page.get_by_test_id(f"fila-empleado-{numero}")
    expect(fila).to_contain_text("Analista Senior")
    expect(fila).to_contain_text("Finanzas")
    expect(page.get_by_test_id(f"estado-empleado-{numero}")).to_have_text("Activo")


def test_cp04_numero_empleado_no_se_modifica_al_editar(page, url_api, url_web):
    """CP-04: El número de empleado y el correo no se modifican al editar."""
    tag = _etiqueta()
    empleado = _crear_empleado(url_api, f"Ana López {tag}", "Analista", "Ventas")
    numero = empleado["numero_empleado"]

    page.goto(url_web)
    expect(page.get_by_test_id(f"fila-empleado-{numero}")).to_be_visible()
    page.get_by_test_id(f"editar-empleado-{numero}").click()
    formulario = _formulario_edicion(page, numero)
    formulario.get_by_test_id("empleado-puesto").fill("Analista")
    formulario.get_by_test_id("empleado-departamento").select_option("Operaciones")
    formulario.get_by_test_id("empleado-guardar").click()

    expect(page.get_by_test_id("mensaje-exito")).to_be_visible()
    expect(page.get_by_test_id(f"numero-empleado-{numero}")).to_have_text(numero)


def test_cp06_rechazar_edicion_con_puesto_invalido(page, url_api, url_web):
    """CP-06: Rechazar la edición con un puesto inválido."""
    tag = _etiqueta()
    empleado = _crear_empleado(url_api, f"Jorge Ruiz {tag}", "Analista", "Tecnología")
    numero = empleado["numero_empleado"]

    page.goto(url_web)
    expect(page.get_by_test_id(f"fila-empleado-{numero}")).to_be_visible()
    page.get_by_test_id(f"editar-empleado-{numero}").click()
    formulario = _formulario_edicion(page, numero)
    formulario.get_by_test_id("empleado-puesto").fill("A")
    formulario.get_by_test_id("empleado-departamento").select_option("Tecnología")
    formulario.get_by_test_id("empleado-guardar").click()

    mensaje_error = formulario.get_by_test_id("mensaje-error")
    expect(mensaje_error).to_be_visible()
    expect(mensaje_error).to_contain_text("puesto")


@pytest.mark.skip(
    reason=(
        "CP-08 no es automatizable vía UI: data-testid=empleado-departamento es un "
        "<select> que solo ofrece los departamentos del catálogo (/api/departamentos); "
        "'Marketing' no es una opción seleccionable, por lo que select_option() nunca "
        "puede elegirlo (timeout). El caso de rechazo de departamento inválido ya queda "
        "cubierto a nivel api en CP-07."
    )
)
def test_cp08_rechazar_edicion_con_departamento_invalido(page, url_api, url_web):
    """CP-08: Rechazar la edición con un departamento inválido."""
    tag = _etiqueta()
    empleado = _crear_empleado(url_api, f"Iván Soto {tag}", "Analista", "Tecnología")
    numero = empleado["numero_empleado"]

    page.goto(url_web)
    expect(page.get_by_test_id(f"fila-empleado-{numero}")).to_be_visible()
    page.get_by_test_id(f"editar-empleado-{numero}").click()
    formulario = _formulario_edicion(page, numero)
    formulario.get_by_test_id("empleado-puesto").fill("Analista")
    formulario.get_by_test_id("empleado-departamento").select_option("Marketing")
    formulario.get_by_test_id("empleado-guardar").click()

    mensaje_error = formulario.get_by_test_id("mensaje-error")
    expect(mensaje_error).to_be_visible()
    expect(mensaje_error).to_contain_text("departamento")


def test_cp10_rechazar_edicion_de_empleado_dado_de_baja(page, url_api, url_web):
    """CP-10: Rechazar la edición de un empleado dado de baja.

    El botón "Editar" aparece deshabilitado para un empleado en estado "baja"
    (comportamiento correcto del criterio de aceptación), así que la prueba
    verifica la deshabilitación en lugar de intentar hacer clic en él.
    """
    tag = _etiqueta()
    empleado = _crear_empleado(url_api, f"Sofía Torres {tag}", "Analista", "Finanzas")
    numero = empleado["numero_empleado"]
    _dar_de_baja(url_api, numero, date.today().isoformat())

    page.goto(url_web)
    expect(page.get_by_test_id(f"estado-empleado-{numero}")).to_have_text("Baja")
    expect(page.get_by_test_id(f"editar-empleado-{numero}")).to_be_disabled()


def test_cp12_dar_de_baja_a_un_empleado_activo(page, url_api, url_web):
    """CP-12: Dar de baja a un empleado activo."""
    tag = _etiqueta()
    empleado = _crear_empleado(url_api, f"Marco Vidal {tag}", "Analista", "Operaciones")
    numero = empleado["numero_empleado"]
    fecha_baja = date.today().isoformat()

    page.goto(url_web)
    expect(page.get_by_test_id(f"fila-empleado-{numero}")).to_be_visible()
    page.get_by_test_id(f"baja-empleado-{numero}").click()
    formulario = _formulario_baja(page, numero)
    formulario.get_by_test_id("empleado-fecha-baja").fill(fecha_baja)
    formulario.get_by_test_id("confirmar-baja").click()

    expect(page.get_by_test_id("mensaje-exito")).to_be_visible()
    expect(page.get_by_test_id(f"estado-empleado-{numero}")).to_have_text("Baja")
    expect(page.get_by_test_id(f"fila-empleado-{numero}")).to_be_visible()


def test_cp14_rechazar_baja_con_fecha_anterior_a_fecha_ingreso(page, url_api, url_web):
    """CP-14: Rechazar la baja con una fecha de baja anterior a la fecha de ingreso."""
    tag = _etiqueta()
    empleado = _crear_empleado(url_api, f"Elena Ríos {tag}", "Analista", "Tecnología")
    numero = empleado["numero_empleado"]
    fecha_baja = (date.today() - timedelta(days=30)).isoformat()

    page.goto(url_web)
    expect(page.get_by_test_id(f"fila-empleado-{numero}")).to_be_visible()
    page.get_by_test_id(f"baja-empleado-{numero}").click()
    page.get_by_test_id("empleado-fecha-baja").fill(fecha_baja)
    page.get_by_test_id("confirmar-baja").click()

    mensaje_error = page.get_by_test_id("mensaje-error")
    expect(mensaje_error).to_be_visible()
    expect(mensaje_error).to_contain_text("fecha de baja")
    expect(page.get_by_test_id(f"estado-empleado-{numero}")).to_have_text("Activo")
