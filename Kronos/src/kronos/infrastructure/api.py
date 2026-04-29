"""
API FastAPI del sistema.

Capa de transporte HTTP que expone el Policy Engine
sin lógica de negocio.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from kronos.infrastructure.routers import decision_router
from kronos.infrastructure.routers import user
from kronos.infrastructure.routers import voice
from kronos.infrastructure.routers import voice_commands
from kronos.infrastructure.routers import emergency
from kronos.infrastructure.routers import monitoring

app = FastAPI(
    title="Kronos API",
    description="Sistema de Asistencia para Motociclistas Urbanos",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(decision_router, prefix="/api/v1", tags=["decisions"])
app.include_router(voice.router, prefix="/api/v1", tags=["voice"])
app.include_router(user.router, prefix="/api/v1", tags=["user"])
app.include_router(voice_commands.router, prefix="/api/v1", tags=["voice-commands"])
app.include_router(emergency.router, prefix="/api/v1", tags=["emergency"])
app.include_router(monitoring.router, prefix="/api/v1", tags=["monitoring"])


@app.get("/")
async def root():
    """Endpoint raíz."""
    return {"message": "Kronos API", "version": "0.1.0"}


@app.get("/health")
async def health():
    """Endpoint de salud."""
    return {"status": "healthy"}


def create_app() -> FastAPI:
    """Factory para crear la aplicación FastAPI."""
    return app
