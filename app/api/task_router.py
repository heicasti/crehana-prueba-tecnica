# app/api/task_router.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.schemas import task_schemas # Importamos los schemas de tarea
from app.application.services.task_service import TaskService # Importamos el servicio de tarea
from app.application.services.task_list_service import TaskListService # También necesitamos el servicio de lista para validar existencia

router = APIRouter(
    tags=["Tasks"] # Etiqueta para la documentación de Swagger
)

# Dependencia para obtener una instancia del servicio de Task
def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(db)

# Dependencia para obtener una instancia del servicio de TaskList (validaciones)
def get_task_list_service(db: Session = Depends(get_db)) -> TaskListService:
    return TaskListService(db)

# Endpoint para crear una nueva tarea dentro de una lista de tareas específica
@router.post("/", response_model=task_schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: task_schemas.TaskCreate,
    task_service: TaskService = Depends(get_task_service),
    task_list_service: TaskListService = Depends(get_task_list_service)
    ):
    # Es necesaria la validación de la lista 
    if not task_list_service.get_task_list(task.task_list_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lista de tareas no encontrada")
    # Esquema completo al servicio
    return task_service.create_task(task)

@router.get("/{task_id}", response_model=task_schemas.TaskResponse)
def read_task(
    task_id: int,
    service: TaskService = Depends(get_task_service)
    ):
    db_task = service.get_task(task_id)
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
    return db_task

# Endpoint para obtener todas las tareas de una lista específica (filtros)
@router.get("/by-list/{task_list_id}", response_model=List[task_schemas.TaskResponse])
def read_tasks_by_list(
    task_list_id: int,
    completed: Optional[bool] = None,
    priority: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    task_service: TaskService = Depends(get_task_service),
    task_list_service: TaskListService = Depends(get_task_list_service)
    ):
    # Valida que la task_list_id exista
    if not task_list_service.get_task_list(task_list_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lista de tareas no encontrada")

    tasks = task_service.get_tasks_by_list_id(
        task_list_id=task_list_id,
        completed=completed,
        priority=priority,
        skip=skip,
        limit=limit
    )
    return tasks

# Endpoint para actualizar una tarea
@router.put("/{task_id}", response_model=task_schemas.TaskResponse)
def update_task(
    task_id: int,
    task_update: task_schemas.TaskUpdate,
    service: TaskService = Depends(get_task_service)
    ):
    db_task = service.update_task(task_id, task_update)
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
    return db_task

# Endpoint para eliminar una tarea
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    service: TaskService = Depends(get_task_service)
    ):
    if not service.delete_task(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
    return {"message": "Tarea eliminada exitosamente"}

# Endpoint para cambiar el estado de una tarea
@router.patch("/{task_id}/toggle-completion", response_model=task_schemas.TaskResponse)
def toggle_task_completion(
    task_id: int,
    service: TaskService = Depends(get_task_service)
    ):
    db_task = service.toggle_task_completion(task_id)
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")
    return db_task