# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from app.infrastructure.database.connection import engine, Base, get_db
from app.api.task_list_router import router as task_list_router_instance
from app.api.task_router import router as task_router_instance # Importa el router de tareas

# Asegura que las tablas existen si se levanta la app sin ejecutar el script externo
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tasks API Crehana",
    description="API para gestionar listas de tareas",
    version="0.1.0",
)

# Incluye routers
app.include_router(task_list_router_instance, prefix="/task-lists")
app.include_router(task_router_instance, prefix="/tasks")

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI! Application is running."}