# tests/test_task_router.py
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest
from datetime import datetime

def test_create_task_in_list(client: TestClient):
    """
    Prueba la creación exitosa de una tarea en una lista existente.
    """
    # 1. Primero, crea una lista de tareas para asociar la tarea.
    task_list_data = {
        "title": "Lista para Tareas de Prueba",
        "description": "Una lista de tareas creada para testing."
    }
    create_list_response = client.post("/task-lists/", json=task_list_data)
    assert create_list_response.status_code == 201
    task_list_id = create_list_response.json()["id"]

    # 2. Datos para la nueva tarea (task_list_id va en el CUERPO de la solicitud)
    task_data = {
        "title": "Tarea de Ejemplo",
        "description": "Descripción de mi tarea de ejemplo.",
        "status": "pending",
        "priority": 1,
        "task_list_id": task_list_id # ¡IMPORTANTE! task_list_id ahora va en el cuerpo
    }

    # 3. Envía una solicitud POST para crear la tarea.
    # La URL es /tasks/ (porque task_router tiene prefix="/tasks" y el endpoint es "/")
    create_task_response = client.post("/tasks/", json=task_data)

    # 4. Afirmaciones para verificar la respuesta
    assert create_task_response.status_code == 201 # Esperamos 201 Created

    response_data = create_task_response.json()
    assert "id" in response_data
    assert response_data["title"] == task_data["title"]
    assert response_data["description"] == task_data["description"]
    assert response_data["status"] == task_data["status"]
    assert response_data["priority"] == task_data["priority"]
    assert response_data["task_list_id"] == task_list_id # Verifica que se haya asignado correctamente
    assert "created_at" in response_data
    assert "updated_at" in response_data
    # Verifica que las fechas sean válidas y coherentes
    assert datetime.fromisoformat(response_data["created_at"]) <= datetime.utcnow()
    assert datetime.fromisoformat(response_data["updated_at"]) <= datetime.utcnow()


def test_create_task_in_non_existent_list(client: TestClient):
    """
    Prueba que no se puede crear una tarea en una lista que no existe.
    """
    # Intenta crear una tarea en una lista de tareas que no existe
    non_existent_list_id = 99999
    task_data = {
        "title": "Tarea para lista inexistente",
        "description": "Esta tarea no debería crearse.",
        "status": "pending",
        "priority": 2,
        "task_list_id": non_existent_list_id # task_list_id va en el cuerpo
    }

    # La URL es /tasks/
    create_task_response = client.post("/tasks/", json=task_data)

    # La respuesta esperada es 404 Not Found con el mensaje específico
    assert create_task_response.status_code == 404
    assert "detail" in create_task_response.json()
    # El mensaje de error debe coincidir con el unificado en task_router.py
    assert create_task_response.json()["detail"] == "Lista de tareas no encontrada"

def test_read_task_by_id(client: TestClient):
    """
    Prueba la lectura de una tarea por su ID.
    """
    # 1. Crear una lista de tareas
    list_response = client.post("/task-lists/", json={"title": "Lista para leer tarea"})
    list_id = list_response.json()["id"]

    # 2. Crear una tarea en esa lista
    task_data = {
        "title": "Tarea para leer",
        "description": "Descripción de tarea para leer",
        "status": "pending",
        "task_list_id": list_id
    }
    create_response = client.post("/tasks/", json=task_data)
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # 3. Leer la tarea usando su ID
    # La URL es /tasks/{task_id}
    read_response = client.get(f"/tasks/{task_id}")
    assert read_response.status_code == 200
    read_data = read_response.json()

    assert read_data["id"] == task_id
    assert read_data["title"] == task_data["title"]
    assert read_data["task_list_id"] == list_id

def test_read_non_existent_task(client: TestClient):
    """
    Prueba que no se puede leer una tarea que no existe.
    """
    non_existent_task_id = 99999
    read_response = client.get(f"/tasks/{non_existent_task_id}")
    assert read_response.status_code == 404
    assert read_response.json()["detail"] == "Tarea no encontrada"

def test_read_tasks_by_list_id(client: TestClient):
    """
    Prueba la lectura de todas las tareas de una lista específica.
    """
    # 1. Crear dos listas de tareas
    list1_response = client.post("/task-lists/", json={"title": "Lista 1 para tareas"})
    list1_id = list1_response.json()["id"]
    list2_response = client.post("/task-lists/", json={"title": "Lista 2 para tareas"})
    list2_id = list2_response.json()["id"]

    # 2. Crear tareas en la Lista 1
    task1_data = {"title": "Tarea 1 L1", "task_list_id": list1_id, "status": "pending", "priority": 1}
    task2_data = {"title": "Tarea 2 L1", "task_list_id": list1_id, "status": "completed", "priority": 2}
    client.post("/tasks/", json=task1_data)
    client.post("/tasks/", json=task2_data)

    # 3. Crear tareas en la Lista 2
    task3_data = {"title": "Tarea 3 L2", "task_list_id": list2_id, "status": "pending", "priority": 1}
    client.post("/tasks/", json=task3_data)

    # 4. Leer tareas de la Lista 1
    # La URL es /tasks/by-list/{task_list_id}
    read_response = client.get(f"/tasks/by-list/{list1_id}")
    assert read_response.status_code == 200
    tasks = read_response.json()
    assert len(tasks) == 2
    assert any(t["title"] == "Tarea 1 L1" for t in tasks)
    assert any(t["title"] == "Tarea 2 L1" for t in tasks)

    # 5. Leer tareas de la Lista 2
    read_response = client.get(f"/tasks/by-list/{list2_id}")
    assert read_response.status_code == 200
    tasks = read_response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Tarea 3 L2"

def test_read_tasks_by_list_id_with_filters(client: TestClient):
    """
    Prueba la lectura de tareas de una lista con filtros (completed y priority).
    """
    list_response = client.post("/task-lists/", json={"title": "Lista con filtros"})
    list_id = list_response.json()["id"]

    # Crear varias tareas con diferentes estados y prioridades
    client.post("/tasks/", json={"title": "Tarea P1", "task_list_id": list_id, "status": "pending", "priority": 1})
    client.post("/tasks/", json={"title": "Tarea P2", "task_list_id": list_id, "status": "pending", "priority": 2})
    client.post("/tasks/", json={"title": "Tarea C1", "task_list_id": list_id, "status": "completed", "priority": 1})
    client.post("/tasks/", json={"title": "Tarea C3", "task_list_id": list_id, "status": "completed", "priority": 3})

    # Filtrar por complet (pendiente)