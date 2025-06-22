# tests/test_task_list_router.py
import time
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest
from app.domain.models import TaskList

def test_create_task_list(client: TestClient, db_session: Session):
    # Datos para crear una lista de tareas
    task_list_data = {
        "title": "Mi Primera Lista de Pruebas",
        "description": "Descripción para una lista de pruebas."
    }

    # Solicitud POST al endpoint de creación de listas de tareas
    response = client.post("/task-lists/", json=task_list_data)

    # Afirmaciones para verificar la respuesta
    assert response.status_code == 201 # El código de estado esperado para creación exitosa

    # Verifica los datos de la respuesta
    response_data = response.json()
    assert response_data["title"] == task_list_data["title"]
    assert response_data["description"] == task_list_data["description"]
    assert "id" in response_data
    assert "created_at" in response_data
    assert "updated_at" in response_data
    assert response_data["completion_percentage"] == 0.0

    # Opcional: Verifica que la lista de tareas realmente se haya guardado en la DB de prueba
    db_task_list = db_session.query(TaskList).filter(TaskList.id == response_data["id"]).first()
    assert db_task_list is not None
    assert db_task_list.title == task_list_data["title"]

def test_get_task_list_by_id(client: TestClient, db_session: Session):
    # 1. Crear una lista de tareas de antemano para poder obtenerla
    task_list_data = {
        "title": "Lista para Obtener",
        "description": "Descripción para la lista que queremos recuperar."
    }
    create_response = client.post("/task-lists/", json=task_list_data)
    assert create_response.status_code == 201
    created_task_list_id = create_response.json()["id"]

    # 2. Intentar obtener la lista de tareas por su ID
    get_response = client.get(f"/task-lists/{created_task_list_id}")

    # 3. Afirmaciones para verificar la respuesta de la obtención
    assert get_response.status_code == 200 # El código de estado esperado para obtención exitosa

    response_data = get_response.json()
    assert response_data["id"] == created_task_list_id
    assert response_data["title"] == task_list_data["title"]
    assert response_data["description"] == task_list_data["description"]
    assert "created_at" in response_data
    assert "updated_at" in response_data
    assert response_data["completion_percentage"] == 0.0

    # Opcional: Verificar si el objeto existe en la DB (aunque ya lo hace la API)
    db_task_list = db_session.query(TaskList).filter(TaskList.id == created_task_list_id).first()
    assert db_task_list is not None
    assert db_task_list.title == task_list_data["title"]

def test_get_non_existent_task_list(client: TestClient):
    # Intentar obtener una lista de tareas con un ID que no existe
    non_existent_id = 99999 # Un ID que sabemos que no existirá en una DB limpia

    get_response = client.get(f"/task-lists/{non_existent_id}")

    # La respuesta esperada es 404 Not Found
    assert get_response.status_code == 404
    assert "detail" in get_response.json()
    assert get_response.json()["detail"] == "Lista de tareas no encontrada"

def test_update_task_list(client: TestClient, db_session: Session):
    # 1. Crear una lista de tareas de antemano para poder actualizarla
    initial_data = {
        "title": "Lista Original",
        "description": "Descripción original de la lista."
    }
    create_response = client.post("/task-lists/", json=initial_data)
    assert create_response.status_code == 201
    created_task_list_id = create_response.json()["id"]
    # Captura created_at como un objeto datetime
    created_at_dt = datetime.fromisoformat(create_response.json()["created_at"])

    # Introduce un pequeño retraso para asegurar que los timestamps sean diferentes
    time.sleep(1)

    # 2. Datos para actualizar la lista de tareas
    update_data = {
        "title": "Lista Actualizada",
        "description": "Nueva descripción de la lista."
    }

    # Envía una solicitud PUT (o PATCH, dependiendo de la implementación) al endpoint de actualización
    # PUT para actualización completa.
    update_response = client.put(f"/task-lists/{created_task_list_id}", json=update_data)

    # 3. Afirmaciones para verificar la respuesta de la actualización
    assert update_response.status_code == 200 # Código de estado esperado para actualización exitosa

    response_data = update_response.json()
    assert response_data["id"] == created_task_list_id
    assert response_data["title"] == update_data["title"]
    assert response_data["description"] == update_data["description"]
    assert "created_at" in response_data
    assert "updated_at" in response_data
    assert response_data["created_at"] != response_data["updated_at"] # updated_at debería ser diferente si hay cambios
    assert response_data["completion_percentage"] == 0.0 # No debería cambiar con esta actualización

    # Compara los objetos datetime directamente asegurando que updated_at sea posterior
    updated_at_dt = datetime.fromisoformat(response_data["updated_at"])
    assert updated_at_dt > created_at_dt # updated_at debería ser estrictamente posterior

    assert response_data["completion_percentage"] == 0.0

    # Opcional: Verificar que la lista de tareas realmente se haya actualizado en la DB de prueba
    db_task_list = db_session.query(TaskList).filter(TaskList.id == created_task_list_id).first()
    assert db_task_list is not None
    assert db_task_list.title == update_data["title"]
    assert db_task_list.description == update_data["description"]

def test_update_non_existent_task_list(client: TestClient):
    # Intentar actualizar una lista de tareas con un ID que no existe
    non_existent_id = 99999
    update_data = {
        "title": "Intento de Actualizar",
        "description": "Esto no debería funcionar."
    }

    update_response = client.put(f"/task-lists/{non_existent_id}", json=update_data)

    # La respuesta esperada es 404 Not Found
    assert update_response.status_code == 404
    assert "detail" in update_response.json()
    assert update_response.json()["detail"] == "Lista de tareas no encontrada"

def test_delete_task_list(client: TestClient, db_session: Session):
    # 1. Crear una lista de tareas para eliminar
    task_list_data = {
        "title": "Lista para Eliminar",
        "description": "Descripción de la lista a borrar."
    }
    create_response = client.post("/task-lists/", json=task_list_data)
    assert create_response.status_code == 201
    created_task_list_id = create_response.json()["id"]

    # 2. Intentar eliminar la lista de tareas
    delete_response = client.delete(f"/task-lists/{created_task_list_id}")

    # 3. Afirmaciones para verificar la respuesta de la eliminación
    assert delete_response.status_code == 204 # Código de estado esperado para eliminación exitosa (No Content)

    # 4. Verificar que la lista de tareas ya no exista en la DB
    from app.domain.models import TaskList
    db_task_list = db_session.query(TaskList).filter(TaskList.id == created_task_list_id).first()
    assert db_task_list is None # La lista no debería estar en la base de datos

    # Opcional: Intentar obtenerla de nuevo a través de la API para confirmar el 404
    get_response_after_delete = client.get(f"/task-lists/{created_task_list_id}")
    assert get_response_after_delete.status_code == 404
    assert get_response_after_delete.json()["detail"] == "Lista de tareas no encontrada"

def test_delete_non_existent_task_list(client: TestClient):
    # Intentar eliminar una lista de tareas con un ID que no existe
    non_existent_id = 99999
    delete_response = client.delete(f"/task-lists/{non_existent_id}")

    # La respuesta esperada es 404 Not Found
    assert delete_response.status_code == 404
    assert "detail" in delete_response.json()
    assert delete_response.json()["detail"] == "Lista de tareas no encontrada"

def test_get_all_task_lists_empty(client: TestClient):
    # Asegurar que no haya listas de tareas antes de empezar esta prueba
    # Esto se maneja bien con los fixtures, que limpian la DB por cada test
    response = client.get("/task-lists/")
    assert response.status_code == 200
    assert response.json() == [] # Esperamos una lista vacía si no hay tareas

def test_get_all_task_lists(client: TestClient):
    # 1. Crear varias listas de tareas
    task_list_data_1 = {"title": "Lista Uno", "description": "Descripción Uno"}
    task_list_data_2 = {"title": "Lista Dos", "description": "Descripción Dos"}
    task_list_data_3 = {"title": "Lista Tres", "description": "Descripción Tres"}

    # La base de datos se limpia entre pruebas, así que creamos aquí lo necesario
    create_response_1 = client.post("/task-lists/", json=task_list_data_1)
    create_response_2 = client.post("/task-lists/", json=task_list_data_2)
    create_response_3 = client.post("/task-lists/", json=task_list_data_3)

    assert create_response_1.status_code == 201
    assert create_response_2.status_code == 201
    assert create_response_3.status_code == 201

    # 2. Intentar obtener todas las listas de tareas
    get_all_response = client.get("/task-lists/")

    # 3. Afirmaciones
    assert get_all_response.status_code == 200
    response_data = get_all_response.json()

    # Esperamos 3 listas
    assert len(response_data) == 3

    # Verifica que los datos de las listas creadas estén presentes y sean correctos
    # No se puede asegurar el orden, así que se verifica la existencia
    titles = [item["title"] for item in response_data]
    assert "Lista Uno" in titles
    assert "Lista Dos" in titles
    assert "Lista Tres" in titles

    # Opcional: Verificar estructura de los items
    for item in response_data:
        assert "id" in item
        assert "title" in item
        assert "description" in item
        assert "created_at" in item
        assert "updated_at" in item
        assert "completion_percentage" in item