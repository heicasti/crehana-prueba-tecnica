# API de Gestión de Tareas (Desafío Técnico Crehana)

## Descripción del Proyecto
Este proyecto implementa una API RESTful para gestionar listas de tareas y tareas individuales dentro de ellas. Desarrollado con FastAPI y Python, sigue las buenas prácticas de diseño y calidad de código, incluyendo una arquitectura limpia por capas (Domain, Application/UseCases, Infrastructure) y tipado fuerte con Pydantic.

## Requisitos

Para ejecutar el proyecto, necesitarás tener instalado:
* **Docker** y **Docker Compose**
* Python 3.9+ (para referencia o desarrollo local si aplicara, pero la ejecución principal es con Docker)

## Configuración y Ejecución de la Aplicación (con Docker Compose)

Esta es la forma recomendada de levantar la aplicación y su base de datos.

1.  **Clonar el Repositorio (si aplica):**
    ```bash
    # Si estás trabajando con Git, clona el repositorio.
    # git clone <URL_DEL_REPOSITORIO>
    # cd <NOMBRE_DEL_REPOSITORIO>
    ```

2.  **Configurar Variables de Entorno:**
    Crea un archivo `.env` en la raíz de tu proyecto (al mismo nivel que `docker-compose.yml`) y añade las siguientes variables.

    ```env
    MYSQL_ROOT_PASSWORD=pass_crehana_secure
    MYSQL_DATABASE=crehana_db
    MYSQL_USER=user_crehana
    MYSQL_PASSWORD=password_crehana
    DATABASE_URL=mysql+pymysql://user_crehana:password_crehana@db_service_mysql:3306/crehana_db
    ```

3.  **Levantar los Servicios:**
    Este comando construirá las imágenes (si hay cambios en el `Dockerfile`), levantará el servicio de base de datos MySQL y la aplicación FastAPI. La base de datos se inicializará y las tablas se crearán automáticamente al iniciar la aplicación web.

    ```bash
    docker compose up --build -d
    ```
    *Espera unos segundos (10-20 segundos) después de ejecutar este comando para que la base de datos se inicialice completamente y el servicio web inicie.*

4.  **Verificar el Estado de los Servicios:**
    Puedes comprobar que ambos contenedores están corriendo y la base de datos está saludable con:
    ```bash
    docker compose ps
    ```
    Deberías ver `db_service_mysql` y `web` en estado `Up (healthy)` o al menos `Up`.

5.  **Acceder a la API:**
    Una vez que los servicios estén corriendo, la API estará disponible en `http://localhost:8000`.
    * **Documentación interactiva (Swagger UI):** `http://localhost:8000/docs`
    * **Documentación alternativa (ReDoc):** `http://localhost:8000/redoc`

## Ejecución de Pruebas

Para correr los tests unitarios y de integración dentro del contenedor `web` (asegúrate de que los servicios estén levantados con `docker compose up -d`):

```bash
docker compose exec web pytest

Para ver el reporte de cobertura de código (se espera un mínimo de 75%):

```bash
docker compose exec web pytest --cov=app

## Buenas Prácticas y Decisiones Técnicas Clave
Arquitectura por Capas: Separación de responsabilidades en Dominio, Aplicación e Infraestructura para facilitar la modularidad, el mantenimiento y la escalabilidad del código.

Tipado Fuerte y Validaciones: Uso extensivo de Pydantic para la definición de esquemas de datos y validaciones automáticas, mejorando la robustez de la API.

Contenedorización (Docker): Utilización de Docker y Docker Compose para crear un entorno de desarrollo consistente, reproducible y portable, facilitando el despliegue de la aplicación y la base de datos.

Persistencia de Datos: Configuración de volúmenes en Docker para asegurar que los datos de la base de datos MySQL persistan incluso si los contenedores son eliminados.

Gestión de Dependencias: Uso de requirements.txt para manejar las dependencias de Python de manera estandarizada.
Testing Automatizado: Implementación de pruebas unitarias y de integración con pytest para verificar la funcionalidad y prevenir regresiones.

Orquestación de Inicio: Uso de depends_on con condition: service_healthy en Docker Compose para asegurar que la aplicación web no intente conectarse a la base de datos hasta que esta esté completamente operativa.

Creación de Tablas al Inicio: El comando de inicio del servicio web incluye la ejecución de un script para crear las tablas de la base de datos automáticamente, simplificando la configuración inicial.

## Pendientes y Mejoras Futuras

Dadas las limitaciones de tiempo de la prueba técnica, se priorizó la implementación de los requisitos principales de CRUD de tareas y listas, la configuración de la infraestructura con Docker y la conexión a la base de datos, así como la integración de las pruebas.

Los siguientes puntos quedarían como mejoras o funcionalidades a implementar en el futuro:

Autenticación y Autorización: Implementación de un sistema de login con JWT para proteger los endpoints de la API.
Asignación de Tareas: Desarrollar la funcionalidad para asignar tareas a usuarios específicos.
Notificaciones Ficticias: Simular el envío de correos electrónicos para notificaciones (e.g., invitaciones).
Cobertura de Tests: Aumentar la cobertura de los tests unitarios, especialmente en los módulos de servicio y enrutamiento, para alcanzar un nivel más alto de confianza. (Nota: La prueba requería 75% de cobertura, se ha logrado, pero siempre se puede mejorar).