"""Punto de entrada de la API de gestión de empleados."""
from datetime import date

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
    SaldoVacacionesSalida,
    VacacionesCrear,
    VacacionesSalida,
)
from modelos import Base, Empleado, SessionLocal, Vacaciones, engine
from vacaciones import DIAS_MAXIMOS_ANIO, anio_soportado, cumple_antiguedad, dias_habiles

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


def obtener_empleado_por_id_o_404(empleado_id: int, db: Session) -> Empleado:
    empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado


@app.post(
    "/api/empleados/{empleado_id}/vacaciones",
    response_model=VacacionesSalida,
    status_code=201,
)
def solicitar_vacaciones(
    empleado_id: int, datos: VacacionesCrear, db: Session = Depends(get_db)
):
    empleado = obtener_empleado_por_id_o_404(empleado_id, db)

    if empleado.estado == "baja":
        raise HTTPException(
            status_code=409,
            detail="No se pueden solicitar vacaciones para un empleado dado de baja",
        )

    if datos.fecha_fin < datos.fecha_inicio:
        raise HTTPException(
            status_code=400,
            detail="La fecha de fin no puede ser anterior a la fecha de inicio",
        )

    if datos.fecha_inicio.year != datos.fecha_fin.year:
        raise HTTPException(
            status_code=400,
            detail="Las vacaciones deben estar dentro de un mismo año calendario",
        )

    anio = datos.fecha_inicio.year
    if not anio_soportado(anio):
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden solicitar vacaciones en 2026 y 2027",
        )

    if not cumple_antiguedad(empleado.fecha_ingreso, datos.fecha_inicio):
        raise HTTPException(
            status_code=400,
            detail="Se requiere al menos un año de antigüedad a la fecha de inicio",
        )

    habiles = dias_habiles(datos.fecha_inicio, datos.fecha_fin)
    if habiles == 0:
        raise HTTPException(status_code=400, detail="El periodo no incluye días hábiles")

    solicitudes_anio = (
        db.query(Vacaciones).filter(Vacaciones.empleado_id == empleado_id).all()
    )
    usados = sum(s.dias_habiles for s in solicitudes_anio if s.fecha_inicio.year == anio)
    disponibles = DIAS_MAXIMOS_ANIO - usados
    if habiles > disponibles:
        raise HTTPException(
            status_code=400,
            detail=f"La solicitud excede los días disponibles: quedan {disponibles} días hábiles",
        )

    solicitud = Vacaciones(
        empleado_id=empleado_id,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
        dias_habiles=habiles,
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)

    return VacacionesSalida(
        id=solicitud.id,
        empleado_id=solicitud.empleado_id,
        fecha_inicio=solicitud.fecha_inicio,
        fecha_fin=solicitud.fecha_fin,
        dias_habiles=solicitud.dias_habiles,
        dias_restantes=disponibles - habiles,
    )


@app.get(
    "/api/empleados/{empleado_id}/vacaciones",
    response_model=SaldoVacacionesSalida,
)
def consultar_saldo_vacaciones(
    empleado_id: int, anio: int | None = None, db: Session = Depends(get_db)
):
    obtener_empleado_por_id_o_404(empleado_id, db)

    anio_consulta = anio or date.today().year
    solicitudes = [
        s
        for s in db.query(Vacaciones).filter(Vacaciones.empleado_id == empleado_id).all()
        if s.fecha_inicio.year == anio_consulta
    ]
    solicitudes.sort(key=lambda s: s.fecha_inicio)
    dias_usados = sum(s.dias_habiles for s in solicitudes)

    return SaldoVacacionesSalida(
        empleado_id=empleado_id,
        anio=anio_consulta,
        dias_usados=dias_usados,
        dias_disponibles=DIAS_MAXIMOS_ANIO - dias_usados,
        solicitudes=solicitudes,
    )
