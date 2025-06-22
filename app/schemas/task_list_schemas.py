# app/schemas/task_list_schemas.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# Schema de Task para la relación
class TaskResponseForList(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    priority: int
    task_list_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schema base para TaskList (atributos básicos para creación y actualización)
class TaskListBase(BaseModel):
    title: str = Field(..., max_length=255, description="Título de la lista de tareas.")
    description: Optional[str] = Field(None, max_length=500, description="Descripción de la lista de tareas.")

# Schema para la creación de una TaskList (hereda de Base)
class TaskListCreate(TaskListBase):
    pass

# Schema para la actualización de una TaskList (todos los campos opcionales)
class TaskListUpdate(TaskListBase):
    title: Optional[str] = Field(None, max_length=255, description="Nuevo título de la lista de tareas.")
    description: Optional[str] = Field(None, max_length=500, description="Nueva descripción de la lista de tareas.")

# Schema para la lectura/respuesta de una TaskList (ID y fechas)
class TaskListResponse(TaskListBase):
    id: int
    created_at: datetime
    updated_at: datetime
    completion_percentage: float = Field(0.0, description="Porcentaje de tareas completadas en la lista.")

    class Config:
        from_attributes = True # Permite que Pydantic lea de instancias ORM

# Schema para incluir tareas dentro de TaskListResponse (para relaciones)
class TaskListResponseWithTasks(TaskListResponse):
    tasks: List[TaskResponseForList] = [] # Una lista de TaskResponse