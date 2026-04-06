from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.usuario import UsuarioCreate, UsuarioResponse, Token
from app.services import usuario_service
from app.core.security import verify_password, create_access_token
import jwt
import os

router = APIRouter(prefix="/usuarios", tags=["Autenticación y Usuarios"])

# Esquema para extraer el token del header "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/login")
SECRET_KEY = os.getenv("SECRET_KEY", "tu_super_secreto_jwt_aqui")
ALGORITHM = "HS256"

@router.post("/registro", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def registrar_usuario(usuario: UsuarioCreate):
    usuario_existente = await usuario_service.get_usuario_por_nombre(usuario.nombre_usuario)
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")
    
    nuevo_usuario = await usuario_service.crear_usuario(usuario)
    return nuevo_usuario

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    usuario = await usuario_service.get_usuario_por_nombre(form_data.username)
    
    if not usuario or not verify_password(form_data.password, usuario["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # El token guardará el ID del usuario en el campo "sub" (subject)
    access_token = create_access_token(data={"sub": str(usuario["id"])})
    return {"access_token": access_token, "token_type": "bearer"}

# Esta dependencia la usaremos en la Fase 4 para las rutas protegidas de Recetas
async def obtener_usuario_actual(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return int(user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ha expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")
