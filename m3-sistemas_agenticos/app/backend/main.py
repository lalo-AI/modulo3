"""Punto de entrada de la API de gestión de empleados."""
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from esquemas import (
    DEPARTAMENTOS_VALIDOS,
    EmpleadoBaja,
    EmpleadoCrear,
    EmpleadoEditar,
    EmpleadoSalida,
)
from modelos import Base, Empleado, SessionLocal, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gestión de empleados")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(request: Request, exc: RequestValidationError):
    """Convierte los errores de Pydantic en {"detail": "mensaje en español"}."""
    primer_error = exc.errors()[0]
    mensaje = str(primer_error.get("msg", "Datos inválidos"))
    prefijo = "Value error, "
    if mensaje.startswith(prefijo):
        mensaje = mensaje[len(prefijo):]
    return JSONResponse(status_code=422, content={"detail": mensaje})


@app.get("/api/salud")
def salud():
    return {"estado": "ok"}


@app.get("/api/departamentos")
def departamentos():
    return DEPARTAMENTOS_VALIDOS


def obtener_empleado_o_404(numero_empleado: str, db: Session) -> Empleado:
    empleado = (
        db.query(Empleado).filter(Empleado.numero_empleado == numero_empleado).first()
    )
    if not empleado:
        raise HTTPException(status_code=404, detail="El empleado no existe")
    return empleado


@app.get("/api/empleados", response_model=list[EmpleadoSalida])
def listar_empleados(
    buscar: str | None = None,
    departamento: str | None = None,
    db: Session = Depends(get_db),
):
    consulta = db.query(Empleado)
    if buscar:
        patron = f"%{buscar.strip().lower()}%"
        consulta = consulta.filter(
            func.lower(Empleado.nombre).like(patron) | func.lower(Empleado.correo).like(patron)
        )
    if departamento:
        consulta = consulta.filter(Empleado.departamento == departamento)
    return consulta.order_by(Empleado.id).all()


@app.post("/api/empleados", response_model=EmpleadoSalida, status_code=201)
def crear_empleado(datos: EmpleadoCrear, db: Session = Depends(get_db)):
    existente = db.query(Empleado).filter(Empleado.correo == datos.correo).first()
    if existente:
        raise HTTPException(status_code=409, detail="El correo ya está registrado")

    total_empleados = db.query(func.count(Empleado.id)).scalar() or 0
    numero_empleado = f"EMP-{total_empleados + 1:04d}"

    empleado = Empleado(
        numero_empleado=numero_empleado,
        nombre=datos.nombre,
        correo=datos.correo,
        puesto=datos.puesto,
        departamento=datos.departamento,
        fecha_ingreso=datos.fecha_ingreso,
        estado="activo",
    )
    db.add(empleado)
    db.commit()
    db.refresh(empleado)
    return empleado


@app.get("/api/empleados/{numero_empleado}", response_model=EmpleadoSalida)
def obtener_empleado(numero_empleado: str, db: Session = Depends(get_db)):
    return obtener_empleado_o_404(numero_empleado, db)


@app.put("/api/empleados/{numero_empleado}", response_model=EmpleadoSalida)
def editar_empleado(
    numero_empleado: str, datos: EmpleadoEditar, db: Session = Depends(get_db)
):
    empleado = obtener_empleado_o_404(numero_empleado, db)
    if empleado.estado == "baja":
        raise HTTPException(
            status_code=409, detail="No se puede editar a un empleado dado de baja"
        )

    empleado.puesto = datos.puesto
    empleado.departamento = datos.departamento
    db.commit()
    db.refresh(empleado)
    return empleado


@app.put("/api/empleados/{numero_empleado}/baja", response_model=EmpleadoSalida)
def dar_de_baja_empleado(
    numero_empleado: str, datos: EmpleadoBaja, db: Session = Depends(get_db)
):
    empleado = obtener_empleado_o_404(numero_empleado, db)
    if datos.fecha_baja < empleado.fecha_ingreso:
        raise HTTPException(
            status_code=422,
            detail="La fecha de baja no puede ser anterior a la fecha de ingreso",
        )

    empleado.estado = "baja"
    empleado.fecha_baja = datos.fecha_baja
    db.commit()
    db.refresh(empleado)
    return empleado
