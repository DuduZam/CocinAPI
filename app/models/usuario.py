from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UsuarioCreate(BaseModel):
    nombre_usuario: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    genero: Optional[str] = None
    edad: Optional[int] = None

class UsuarioResponse(BaseModel):
    id: int
    nombre_usuario: str
    genero: Optional[str]
    edad: Optional[int]
    fecha_creacion: datetime

class Token(BaseModel):
    access_token: str
    token_type: str