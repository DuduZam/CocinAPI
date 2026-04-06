# app/services/receta_service.py
import json
from app.db.database import db
from app.models.receta import RecetaCreate

async def crear_receta(receta: RecetaCreate, usuario_id: int):
    async with db.pool.acquire() as connection:
        # Iniciamos una transacción
        async with connection.transaction():
            # 1. Insertar la Receta
            query_receta = """
                INSERT INTO recetas (usuario_id, titulo, descripcion, instrucciones, 
                                     tiempo_preparacion, tiempo_coccion, porciones, es_publica)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id, fecha_creacion
            """
            # Convertimos la lista de instrucciones a un string JSON para guardarlo en JSONB
            instrucciones_json = json.dumps(receta.instrucciones)
            
            row_receta = await connection.fetchrow(
                query_receta, usuario_id, receta.titulo, receta.descripcion, 
                instrucciones_json, receta.tiempo_preparacion, receta.tiempo_coccion, 
                receta.porciones, receta.es_publica
            )
            receta_id = row_receta["id"]

            # 2. Insertar los Ingredientes (Usamos executemany para alto rendimiento)
            query_ingredientes = """
                INSERT INTO ingredientes (receta_id, nombre, cantidad, unidad_medida)
                VALUES ($1, $2, $3, $4)
            """
            ingredientes_data = [
                (receta_id, ing.nombre, ing.cantidad, ing.unidad_medida.value) 
                for ing in receta.ingredientes
            ]
            await connection.executemany(query_ingredientes, ingredientes_data)

            # 3. Insertar los Tags (si existen)
            if receta.tags:
                query_tags = "INSERT INTO tag_recetas (receta_id, tag) VALUES ($1, $2)"
                tags_data = [(receta_id, tag.strip().lower()) for tag in receta.tags]
                await connection.executemany(query_tags, tags_data)

            # Retornamos los datos combinados para la respuesta
            return {
                "id": receta_id,
                "usuario_id": usuario_id,
                "fecha_creacion": row_receta["fecha_creacion"],
                **receta.model_dump()
            }

async def eliminar_receta(receta_id: int, usuario_id: int) -> bool:
    # Solo eliminamos si la receta existe y pertenece al usuario actual
    query = "DELETE FROM recetas WHERE id = $1 AND usuario_id = $2 RETURNING id"
    async with db.pool.acquire() as connection:
        deleted_id = await connection.fetchval(query, receta_id, usuario_id)
        return bool(deleted_id)


async def obtener_recetas_publicas(limite: int = 10, offset: int = 0, busqueda: str = None):
    # Retorna una lista paginada de recetas públicas
    query = """
        SELECT id, titulo, descripcion, tiempo_preparacion, tiempo_coccion, porciones, fecha_creacion, usuario_id
        FROM recetas
        WHERE es_publica = TRUE
    """
    parametros = []
    
    if busqueda:
        query += " AND (titulo ILIKE $1 OR descripcion ILIKE $1)"
        parametros.append(f"%{busqueda}%")
        query += " ORDER BY fecha_creacion DESC LIMIT $2 OFFSET $3"
        parametros.extend([limite, offset])
    else:
        query += " ORDER BY fecha_creacion DESC LIMIT $1 OFFSET $2"
        parametros.extend([limite, offset])

    async with db.pool.acquire() as connection:
        filas = await connection.fetch(query, *parametros)
        return [dict(fila) for fila in filas]

async def obtener_receta_por_id(receta_id: int):
    # Obtiene el detalle completo de una receta ensamblando sus 3 tablas
    async with db.pool.acquire() as connection:
        receta_row = await connection.fetchrow("SELECT * FROM recetas WHERE id = $1", receta_id)
        if not receta_row:
            return None
        
        receta_dict = dict(receta_row)
        # Parseamos el JSONB de instrucciones que guardamos como string
        if isinstance(receta_dict.get('instrucciones'), str):
            receta_dict['instrucciones'] = json.loads(receta_dict['instrucciones'])
        
        # Obtenemos ingredientes
        ingredientes_rows = await connection.fetch(
            "SELECT nombre, cantidad, unidad_medida FROM ingredientes WHERE receta_id = $1", receta_id
        )
        receta_dict['ingredientes'] = [dict(ing) for ing in ingredientes_rows]
        
        # Obtenemos tags
        tags_rows = await connection.fetch(
            "SELECT tag FROM tag_recetas WHERE receta_id = $1", receta_id
        )
        receta_dict['tags'] = [tag['tag'] for tag in tags_rows]
        
        return receta_dict