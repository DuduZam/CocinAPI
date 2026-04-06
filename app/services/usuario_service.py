from app.db.database import db
from app.models.usuario import UsuarioCreate
from app.core.security import get_password_hash

async def get_usuario_por_nombre(nombre_usuario: str):
    query = "SELECT * FROM usuarios WHERE nombre_usuario = $1"

    # Conectamos a la base de datos
    async with db.pool.acquire() as connection:
        row = await connection.fetchrow(query, nombre_usuario)
        return dict(row) if row else None

async def crear_usuario(usuario: UsuarioCreate):
    query = """
        INSERT INTO usuarios (nombre_usuario, password_hash, genero, edad)
        VALUES ($1, $2, $3, $4)
        RETURNING id, nombre_usuario, genero, edad, fecha_creacion
    """

    # Conseguimos el hash de la contraseña
    password_hash = get_password_hash(usuario.password)
    
    async with db.pool.acquire() as connection:
        row = await connection.fetchrow(
            query, 
            usuario.nombre_usuario, 
            password_hash, 
            usuario.genero, 
            usuario.edad
        )
        return dict(row)