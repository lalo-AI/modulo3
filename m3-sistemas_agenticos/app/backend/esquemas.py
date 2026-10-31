"""Esquemas Pydantic v2 para la API de empleados."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator

DEPARTAMENTOS_VALIDOS = [
    "Tecnología",
    "Ventas",
    "Finanzas",
    "Recursos Humanos",
    "Operaciones",
]


def _validar_puesto(valor: str) -> str:
    limpio = valor.strip()
    if not (2 <= len(limpio) <= 60):
        raise ValueError("El campo 'puesto' debe tener entre 2 y 60 caracteres")
    return limpio


def _validar_departamento(valor: str) -> str:
    if valor not in DEPARTAMENTOS_VALIDOS:
        raise ValueError(
            "El campo 'departamento' debe ser uno de: " + ", ".join(DEPARTAMENTOS_VALIDOS)
        )
    return valor


class EmpleadoCrear(BaseModel):
    nombre: str
    correo: str
    puesto: str
    departamento: str
    fecha_ingreso: date

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        limpio = valor.strip()
        if not (2 <= len(limpio) <= 80):
            raise ValueError("El campo 'nombre' debe tener entre 2 y 80 caracteres")
        return limpio

    @field_validator("puesto")
    @classmethod
    def validar_puesto(cls, valor: str) -> str:
        return _validar_puesto(valor)

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, valor: str) -> str:
        correo = valor.strip().lower()
        if not correo.endswith("@empresa.com"):
            raise ValueError("Usa el correo corporativo @empresa.com")
        return correo

    @field_validator("departamento")
    @classmethod
    def validar_departamento(cls, valor: str) -> str:
        return _validar_departamento(valor)

    @field_validator("fecha_ingreso")
    @classmethod
    def validar_fecha_ingreso(cls, valor: date) -> date:
        if valor > date.today():
            raise ValueError("La fecha de ingreso no puede ser futura")
        return valor


class EmpleadoEditar(BaseModel):
    puesto: str
    departamento: str

    @field_validator("puesto")
    @classmethod
    def validar_puesto(cls, valor: str) -> str:
        return _validar_puesto(valor)

    @field_validator("departamento")
    @classmethod
    def validar_departamento(cls, valor: str) -> str:
        return _validar_departamento(valor)


class EmpleadoBaja(BaseModel):
    fecha_baja: date


class EmpleadoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero_empleado: str
    nombre: str
    correo: str
    puesto: str
    departamento: str
    fecha_ingreso: date
    estado: str
    fecha_baja: date | None = None
    creado_en: datetime
