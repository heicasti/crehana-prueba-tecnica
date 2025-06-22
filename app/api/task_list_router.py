# app/api/task_list_router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.schemas import task_list_schemas
from app.application.services.task_list_service import TaskListService

router = APIRouter(
    tags=["Task Lists"] # Etiqueta para la documentación de Swagger
)

# Dependencia para obtener una instancia del servicio de TaskList
def get_task_list_service(db: Session = Depends(get_db)) -> TaskListService:
    return TaskListService(db)

# Endpoint para crear una nueva lista de tareas
@router.post("/", response_model=task_list_schemas.TaskListResponse, status_code=status.HTTP_201_CREATED)
def create_task_list(
    task_list: task_list_schemas.TaskListCreate,
    service: TaskListService = Depends(get_task_list_service)
    ):
    return service.create_task_list(task_list)

# Endpoint para obtener una lista de tareas por ID
@router.get("/{task_list_id}", response_model=task_list_schemas.TaskListResponseWithTasks)
def read_task_list(
    task_list_id: int,
    service: TaskListService = Depends(get_task_list_service)
    ):
    db_task_list = service.get_task_list(task_list_id)
    if db_task_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lista de tareas no encontrada")
    return db_task_list

# Endpoint para obtener todas las listas de tareas
@router.get("/", response_model=List[task_list_schemas.TaskListResponse])
def read_all_task_lists(
    skip: int = 0,
    limit: int = 100,
    service: TaskListService = Depends(get_task_list_service)
    ):
    return service.get_all_task_lists(skip=skip, limit=limit)

# Endpoint para actualizar una lista de tareas
@router.put("/{task_list_id}", response_model=task_list_schemas.TaskListResponse)
def update_task_list(
    task_list_id: int,
    task_list_update: task_list_schemas.TaskListUpdate,
    service: TaskListService = Depends(get_task_list_service)
    ):
    db_task_list = service.update_task_list(task_list_id, task_list_update)
    if db_task_list is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lista de tareas no encontrada")
    return db_task_list

# Endpoint para eliminar una lista de tareas
@router.delete("/{task_list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_list(
    task_list_id: int,
    service: TaskListService = Depends(get_task_list_service)
    ):
    if not service.delete_task_list(task_list_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lista de tareas no encontrada")
    return {"message": "Lista de tareas eliminada exitosamente"}