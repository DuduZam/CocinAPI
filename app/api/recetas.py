# app/api/recetas.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.receta import RecetaCreate, RecetaResponse
from app.services import receta_service
from app.api.usuarios import obtener_usuario_actual
from typing import List, Optional

router = APIRouter(prefix="/recetas", tags=["Recetas"])

@router.post("/", response_model=RecetaResponse, status_code=status.HTTP_201_CREATED)
async def crear_nueva_receta(
    receta: RecetaCreate, 
    usuario_id: int = Depends(obtener_usuario_actual) # ¡Protegemos la ruta aquí!
):
    try:
        nueva_receta = await receta_service.crear_receta(receta, usuario_id)
        return nueva_receta
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear la receta: {str(e)}")

@router.delete("/{receta_id}", status_code=status.HTTP_204_NO_CONTENT)
async def borrar_receta(
    receta_id: int, 
    usuario_id: int = Depends(obtener_usuario_actual)
):
    eliminada = await receta_service.eliminar_receta(receta_id, usuario_id)
    if not eliminada:
        raise HTTPException(
            status_code=404, 
            detail="Receta no encontrada o no tienes permisos para eliminarla"
        )
    return None

@router.get("/", status_code=status.HTTP_200_OK)
async def listar_recetas_publicas(
    limite: int = 10, 
    offset: int = 0, 
    busqueda: Optional[str] = None
):
    try:
        recetas = await receta_service.obtener_recetas_publicas(limite, offset, busqueda)
        return recetas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {str(e)}")

@router.get("/{receta_id}", response_model=RecetaResponse, status_code=status.HTTP_200_OK)
async def ver_detalle_receta(receta_id: int):
    receta = await receta_service.obtener_receta_por_id(receta_id)
    if not receta:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    
    # Si la receta es privada, podríamos requerir token aquí, 
    # pero para simplificar, asumimos que este endpoint solo muestra si existe.
    if not receta['es_publica']:
        raise HTTPException(status_code=403, detail="Esta receta es privada")
        
    return receta