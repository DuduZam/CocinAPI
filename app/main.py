# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.database import db
# Importamos las rutas
from app.api import usuarios
from app.api import usuarios, recetas

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Se ejecuta al iniciar la aplicación
    await db.connect()
    await db.execute_init_script()
    yield
    # 2. Se ejecuta al apagar la aplicación
    await db.disconnect()

app = FastAPI(
    title="CocinAPI",
    description="API RESTful de alto rendimiento para gestión de recetas.",
    version="1.0.0",
    lifespan=lifespan
)

# Registrar las rutas de usuarios
app.include_router(usuarios.router)
# Registrar las rutas de recetas
app.include_router(recetas.router)

@app.get("/")
async def root():
    return {"mensaje": "¡Bienvenido a CocinAPI! Todo está funcionando correctamente. 🚀"}
