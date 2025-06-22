# app/application/services/task_list_service.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError
from app.domain import models
from app.schemas import task_list_schemas
from typing import List, Optional

class TaskListService:
    def __init__(self, db: Session):
        self.db = db

    # Calcula el porcentaje de completitud
    def completion_percentage_calculate(self, task_list: models.TaskList) -> float:
        total_tasks = len(task_list.tasks)
        if total_tasks == 0:
            return 0.0
        completed_tasks = sum(1 for task in task_list.tasks if task.completed)
        return (completed_tasks / total_tasks) * 100.0

    def create_task_list(self, task_list: task_list_schemas.TaskListCreate) -> models.TaskList:
        db_task_list = models.TaskList(**task_list.model_dump())
        try:
            self.db.add(db_task_list)
            self.db.commit()
            self.db.refresh(db_task_list)
            db_task_list.completion_percentage = 0.0 # porcentaje es 0.0 por defecto
            return db_task_list
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear la lista de tareas: {e}")

    def get_task_list(self, task_list_id: int) -> Optional[models.TaskList]:
        # Carga las tareas relacionadas en la misma consulta
        db_task_list = self.db.query(models.TaskList).options(joinedload(models.TaskList.tasks)).filter(models.TaskList.id == task_list_id).first()
        if db_task_list:
            db_task_list.completion_percentage = self.completion_percentage_calculate(db_task_list)
        return db_task_list

    def get_all_task_lists(self, skip: int = 0, limit: int = 100) -> List[models.TaskList]:
        # Carga las tareas de todas las listas
        task_lists = self.db.query(models.TaskList).options(joinedload(models.TaskList.tasks)).offset(skip).limit(limit).all()
        for task_list in task_lists:
            task_list.completion_percentage = self.completion_percentage_calculate(task_list)
        return task_lists

    def update_task_list(self, task_list_id: int, task_list_update: task_list_schemas.TaskListUpdate) -> Optional[models.TaskList]:
        # Para actualizar, se cargan las tareas para recalcular el porcentaje después de la actualización
        db_task_list = self.db.query(models.TaskList).options(joinedload(models.TaskList.tasks)).filter(models.TaskList.id == task_list_id).first()
        if db_task_list:
            update_data = task_list_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_task_list, key, value)
            try:
                self.db.add(db_task_list)
                self.db.commit()
                self.db.refresh(db_task_list)
                # Recalcular el porcentaje después de la actualización
                db_task_list.completion_percentage = self.completion_percentage_calculate(db_task_list)
                return db_task_list
            except SQLAlchemyError as e:
                self.db.rollback()
                raise Exception(f"Error al actualizar la lista de tareas: {e}")
        return None

    def delete_task_list(self, task_list_id: int) -> bool:
        db_task_list = self.db.query(models.TaskList).filter(models.TaskList.id == task_list_id).first()
        if db_task_list:
            try:
                self.db.delete(db_task_list)
                self.db.commit()
                return True
            except SQLAlchemyError as e:
                self.db.rollback()
                raise Exception(f"Error al eliminar la lista de tareas: {e}")
        return False