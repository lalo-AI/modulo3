"""Modelo de datos y conexión a la base de datos SQLite."""
import os
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos")
os.makedirs(DATOS_DIR, exist_ok=True)
RUTA_DB = os.path.join(DATOS_DIR, "empleados.db")

engine = create_engine(f"sqlite:///{RUTA_DB}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Empleado(Base):
    __tablename__ = "empleados"

    id = Column(Integer, primary_key=True, index=True)
    numero_empleado = Column(String, unique=True, nullable=False, index=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, unique=True, nullable=False, index=True)
    puesto = Column(String, nullable=False)
    departamento = Column(String, nullable=False)
    fecha_ingreso = Column(Date, nullable=False)
    estado = Column(String, nullable=False, default="activo")
    fecha_baja = Column(Date, nullable=True)
    creado_en = Column(DateTime, nullable=False, default=datetime.utcnow)


class Vacaciones(Base):
    __tablename__ = "vacaciones"

    id = Column(Integer, primary_key=True, index=True)
    empleado_id = Column(Integer, ForeignKey("empleados.id"), nullable=False, index=True)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    dias_habiles = Column(Integer, nullable=False)
