# app/schemas/task_schemas.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# Schema base para Task (atributos básicos para creación y actualización)
class TaskBase(BaseModel):
    title: str = Field(..., max_length=255, description="Título de la tarea.")
    description: Optional[str] = Field(None, max_length=500, description="Descripción de la tarea.")
    completed: bool = Field(False, description="Estado de completitud de la tarea.")
    status: str = "pending"
    priority: int = Field(0, ge=0, le=2, description="Prioridad de la tarea (0=Baja, 1=Media, 2=Alta).")
    task_list_id: int = Field(..., description="ID de la lista de tareas a la que pertenece.")

# Schema para la creación de una Task (herencia de Base)
class TaskCreate(TaskBase):
    task_list_id: int # Se debe incluir

    class Config:
        from_attributes = True

# Schema para la actualización de una Task (todos los campos opcionales)
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255, description="Nuevo título de la tarea.")
    description: Optional[str] = Field(None, max_length=500, description="Nueva descripción de la tarea.")
    completed: Optional[bool] = Field(None, description="Nuevo estado de completitud.")
    priority: Optional[int] = Field(None, ge=0, le=2, description="Nueva prioridad de la tarea.")
    # task_list_id no se actualiza directamente aquí, la tarea pertenece a una lista fija

# Schema para la lectura/respuesta de una Task (ID y fechas)
class TaskResponse(TaskBase):
    id: int
    task_list_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Pydantic lea de instancias ORM