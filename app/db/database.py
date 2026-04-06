# app/db/database.py
import asyncpg
import os
import logging

logger = logging.getLogger(__name__)

# Leemos la variable de entorno que definimos en docker-compose.yml
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://cocinapi_user:supersecreto@db:5432/cocinapi_db"
)

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(DATABASE_URL)
            logger.info("✅ Conexión al Pool de la Base de Datos establecida.")
        except Exception as e:
            logger.error(f"❌ Error conectando a la base de datos: {e}")
            raise e

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            logger.info("🔌 Conexión a la Base de Datos cerrada.")

    async def execute_init_script(self):
        """Lee y ejecuta el archivo init_db.sql para crear las tablas"""
        script_path = os.path.join(os.path.dirname(__file__), "init_db.sql")
        try:
            with open(script_path, "r", encoding="utf-8") as file:
                sql_script = file.read()
            
            async with self.pool.acquire() as connection:
                await connection.execute(sql_script)
            logger.info("✅ Tablas de la base de datos verificadas/creadas con éxito.")
        except Exception as e:
            logger.error(f"❌ Error ejecutando init_db.sql: {e}")

# Instancia global para importar en nuestras rutas y servicios
db = Database()
