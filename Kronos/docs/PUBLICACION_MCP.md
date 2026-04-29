# Publicacion: Kronos y MCP

## Alcance

**Kronos** es una API FastAPI (motor de decision/asistencia para motociclistas). **No** incluye hoy un servidor MCP listo para publicar en un catalogo de herramientas (stdio/HTTP MCP estandar para clientes tipo Cursor).

La integracion MCP descrita en [MCP_INTEGRACION.md](MCP_INTEGRACION.md) y el servicio [bike_specs_mcp_service.py](../src/kronos/infrastructure/services/bike_specs_mcp_service.py) son plan o codigo de refuerzo local sin cliente MCP real.

**Correcto publicar como:** imagen Docker + API documentada ([VERIFICACION.md](VERIFICACION.md), `docker-compose`, Makefile).

**Incorrecto afirmar hoy:** "Kronos es un paquete MCP publicable" sin implementar servidor MCP o cliente oficial.

## Si mas adelante se requiere un MCP publicable

1. Definir transporte (HTTP tipo volunteer-mcp vs stdio).
2. Listar herramientas minimas (ej. ficha moto, decision simplificada).
3. Versionar y documentar en README del paquete.
