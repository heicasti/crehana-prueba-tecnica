# app/application/services/task_service.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.domain import models
from app.schemas import task_schemas

class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def create_task(self, task_create_schema: task_schemas.TaskCreate):
        db_task = models.Task(**task_create_schema.model_dump())
        try:
            self.db.add(db_task)
            self.db.commit()
            self.db.refresh(db_task)
            return db_task
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Error al crear la tarea: {e}")

    def get_task(self, task_id: int) -> Optional[models.Task]:
        return self.db.query(models.Task).filter(models.Task.id == task_id).first()

    def get_tasks_by_list_id(self, task_list_id: int, completed: Optional[bool] = None, priority: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[models.Task]:
        query = self.db.query(models.Task).filter(models.Task.task_list_id == task_list_id)
        if completed is not None:
            query = query.filter(models.Task.completed == completed)
        if priority is not None:
            query = query.filter(models.Task.priority == priority)
        return query.offset(skip).limit(limit).all()

    def update_task(self, task_id: int, task_update: task_schemas.TaskUpdate) -> Optional[models.Task]:
        db_task = self.get_task(task_id)
        if db_task:
            update_data = task_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_task, key, value)
            try:
                self.db.add(db_task)
                self.db.commit()
                self.db.refresh(db_task)
                return db_task
            except SQLAlchemyError as e:
                self.db.rollback()
                raise Exception(f"Error al actualizar la tarea: {e}")
        return None

    def delete_task(self, task_id: int) -> bool:
        db_task = self.get_task(task_id)
        if db_task:
            try:
                self.db.delete(db_task)
                self.db.commit()
                return True
            except SQLAlchemyError as e:
                self.db.rollback()
                raise Exception(f"Error al eliminar la tarea: {e}")
        return False

    def toggle_task_completion(self, task_id: int) -> Optional[models.Task]:
        db_task = self.get_task(task_id)
        if db_task:
            db_task.completed = not db_task.completed
            try:
                self.db.add(db_task)
                self.db.commit()
                self.db.refresh(db_task)
                return db_task
            except SQLAlchemyError as e:
                self.db.rollback()
                raise Exception(f"Error al cambiar estado de la tarea: {e}")
        return None