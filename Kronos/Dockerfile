FROM python:3.11-slim

# Metadatos
LABEL maintainer="Kronos Team"
LABEL description="Sistema de Asistencia para Motociclistas Urbanos"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de configuración de dependencias
COPY pyproject.toml ./

# Instalar dependencias primero
RUN pip install --upgrade pip

# Copiar el código fuente
COPY src/ ./src/
COPY docs/ ./docs/

# Instalar el paquete en modo desarrollo
RUN pip install -e .

# Exponer el puerto
EXPOSE 8000

# Variables de entorno para uvicorn
ENV HOST=0.0.0.0 \
    PORT=8000

# Comando por defecto
CMD ["uvicorn", "kronos.infrastructure.api:app", "--host", "0.0.0.0", "--port", "8000"]
