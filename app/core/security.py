# app/core/security.py
import jwt
import bcrypt
import os
from datetime import datetime, timedelta, timezone

# Configuración JWT
SECRET_KEY = os.getenv("SECRET_KEY", "tu_super_secreto_jwt_aqui")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 semana

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # bcrypt requiere bytes, así que codificamos los strings a utf-8
    password_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)

def get_password_hash(password: str) -> str:
    # Codificamos la contraseña a bytes, generamos la "sal" y hasheamos
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password_bytes = bcrypt.hashpw(password_bytes, salt)
    
    # Decodificamos de nuevo a string para guardarlo en la base de datos (VARCHAR)
    return hashed_password_bytes.decode('utf-8')

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
