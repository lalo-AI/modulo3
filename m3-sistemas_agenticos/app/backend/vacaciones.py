"""Reglas de negocio para las solicitudes de vacaciones (HU-10)."""
from datetime import date, timedelta

DIAS_MAXIMOS_ANIO = 12

# Festivos oficiales (Ley Federal del Trabajo, artículo 74).
FESTIVOS = {
    2026: {
        date(2026, 1, 1),
        date(2026, 2, 2),
        date(2026, 3, 16),
        date(2026, 5, 1),
        date(2026, 9, 16),
        date(2026, 11, 16),
        date(2026, 12, 25),
    },
    2027: {
        date(2027, 1, 1),
        date(2027, 2, 1),
        date(2027, 3, 15),
        date(2027, 5, 1),
        date(2027, 9, 16),
        date(2027, 11, 15),
        date(2027, 12, 25),
    },
}


def anio_soportado(anio: int) -> bool:
    return anio in FESTIVOS


def dias_habiles(fecha_inicio: date, fecha_fin: date) -> int:
    """Cuenta los días hábiles del periodo, incluyendo ambos extremos."""
    festivos = FESTIVOS.get(fecha_inicio.year, set())
    dias = 0
    actual = fecha_inicio
    while actual <= fecha_fin:
        if actual.weekday() < 5 and actual not in festivos:
            dias += 1
        actual += timedelta(days=1)
    return dias


def fecha_aniversario(fecha_ingreso: date) -> date:
    """Fecha en la que el empleado cumple un año desde su ingreso."""
    try:
        return fecha_ingreso.replace(year=fecha_ingreso.year + 1)
    except ValueError:
        # 29 de febrero en un año no bisiesto: el aniversario cae el 1 de marzo.
        return date(fecha_ingreso.year + 1, 3, 1)


def cumple_antiguedad(fecha_ingreso: date, fecha_inicio: date) -> bool:
    return fecha_inicio >= fecha_aniversario(fecha_ingreso)
