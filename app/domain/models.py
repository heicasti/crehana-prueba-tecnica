# app/domain/models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, func, Float # Añade func aquí
from app.infrastructure.database.connection import Base

class TaskList(Base):
    __tablename__ = "task_lists"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    tasks = relationship("Task", back_populates="task_list")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    description = Column(String(500), nullable=True)
    status = Column(String(50), default="pending") # necesario el valor por defecto
    completed = Column(Boolean, default=False)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    task_list_id = Column(Integer, ForeignKey("task_lists.id"), nullable=False)
    task_list = relationship("TaskList", back_populates="tasks")