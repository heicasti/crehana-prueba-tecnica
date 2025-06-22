# Dockerfile
# 1: instala dependencias
FROM python:3.11-slim-bookworm as builder

WORKDIR /app

# 2: Copia el archivo de requisitos e instala las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3: Copia solo lo esencial para ejecutar la aplicación)
FROM python:3.11-slim-bookworm

WORKDIR /app

# 4: Copia las dependencias instaladas de la etapa de construcción
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 5: Copia el código de tu aplicación
COPY . /app

# 6: Expone el puerto que usa FastAPI
EXPOSE 8000

# Comando para ejecutar la aplicación con Uvicorn
# --host 0.0.0.0 es crucial para que la app sea accesible desde fuera del contenedor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]