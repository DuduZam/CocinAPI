# app/models/receta.py
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime

# Definimos el Enum estandarizado
class UnidadMedida(str, Enum):
    CDTA = "cdta"
    CDA = "cda"
    TAZA = "taza"
    ML = "ml"
    L = "l"
    GR = "gr"
    KG = "kg"
    OZ = "oz"
    LB = "lb"
    PIZCA = "pizca"
    PUNADO = "puñado"
    UNIDAD = "unidad"
    PIEZA = "pieza"
    DIENTE = "diente"

class IngredienteBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    cantidad: float = Field(..., gt=0)
    unidad_medida: UnidadMedida

class RecetaCreate(BaseModel):
    titulo: str = Field(..., max_length=255)
    descripcion: Optional[str] = None
    instrucciones: List[str] = Field(..., min_length=1)
    ingredientes: List[IngredienteBase] = Field(..., min_length=1)
    tiempo_preparacion: Optional[int] = Field(None, ge=0)
    tiempo_coccion: Optional[int] = Field(None, ge=0)
    porciones: Optional[int] = Field(None, gt=0)
    tags: Optional[List[str]] = []
    es_publica: bool = False

# Modelo de salida (Response)
class RecetaResponse(RecetaCreate):
    id: int
    usuario_id: int
    fecha_creacion: datetime