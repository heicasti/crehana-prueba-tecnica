# app/create_db_tables.py

from app.infrastructure.database.connection import engine, Base
from domain.models import TaskList, Task

print("Intentando crear las tablas de la base de datos...")

try:
    Base.metadata.create_all(bind=engine)
    print("¡Tablas de la base de datos creadas exitosamente!")
except Exception as e:
    print(f"Error al crear las tablas de la base de datos: {e}")
    print("Asegúrate de que el contenedor MySQL esté funcionando y accesible.")