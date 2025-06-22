# app/infrastructure/database/connection.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Variables de entorno del archivo .env
load_dotenv()

# Obtiene la URL de la base de datos de las variables de entorno
# DATABASE_URL definida .env
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("La variable de entorno DATABASE_URL no está configurada.")

# Crea el motor de la base de datos de SQLAlchemy
# echo=True muestra las sentencias SQL en la consola (depuración)
engine = create_engine(DATABASE_URL, echo=True)

# Crea una clase SessionLocal para cada sesión de base de datos
# autocommit=False para rollback
# autoflush=False para no hacer flush automáticamente
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para tus modelos ORM
Base = declarative_base()

# Dependencia para obtener una sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()