# Guía de Verificación de Kronos

Este documento describe cómo verificar que el servicio Kronos funciona correctamente.

---

## Prerrequisitos

1. **Docker y Docker Compose instalados**
   ```bash
   docker --version
   docker-compose --version
   ```

2. **Docker daemon corriendo**
   ```bash
   docker ps
   ```

---

## Paso 1: Verificar Código (Local)

Antes de construir Docker, puedes verificar que las importaciones del código funcionen:

```bash
# Instalar dependencias localmente (opcional)
pip install -e .

# Verificar importaciones
python scripts/verify_imports.py

# O usando Make
make verify
```

**Nota:** Este paso es opcional. Las dependencias se instalarán automáticamente en Docker.

---

## Paso 2: Construir la Imagen Docker

```bash
# Construir la imagen
docker-compose build

# O usando Make
make build
```

**Verificación:**
```bash
# Verificar que la imagen se creó
docker images | grep kronos
```

---

## Paso 3: Levantar el Servicio

```bash
# Levantar en modo producción
docker-compose up -d

# O usando Make
make up

# Ver logs en tiempo real
docker-compose logs -f kronos-api

# O usando Make
make logs
```

**Verificación:**
```bash
# Verificar que el contenedor está corriendo
docker ps | grep kronos-api
```

---

## Paso 4: Verificar Endpoints

### 4.1 Health Check

```bash
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{"status": "healthy"}
```

### 4.2 Endpoint Raíz

```bash
curl http://localhost:8000/
```

**Respuesta esperada:**
```json
{"message": "Kronos API", "version": "0.1.0"}
```

### 4.3 Endpoint de Decisiones (GET)

```bash
curl http://localhost:8000/api/v1/decisions
```

**Respuesta esperada:**
```json
{
  "decision": "PROCEED",
  "mode": "NORMAL",
  "risk_score": 0.2,
  "risk_level": "LOW",
  "message": "Puedes avanzar con normalidad.",
  "confidence": 0.85
}
```

### 4.4 Endpoint de Decisiones (POST)

```bash
curl -X POST http://localhost:8000/api/v1/decisions
```

**Respuesta esperada:**
Misma estructura que GET.

### 4.5 Documentación Swagger

Abrir en el navegador:
```
http://localhost:8000/docs
```

### 4.6 Documentación ReDoc

Abrir en el navegador:
```
http://localhost:8000/redoc
```

---

## Paso 5: Pruebas Automatizadas

### Pruebas de API (Requiere dependencias instaladas localmente)

```bash
# Instalar dependencias localmente primero
pip install -e ".[dev]"

# Ejecutar pruebas de API
python scripts/test_api.py

# O usando Make
make test-api
```

---

## Solución de Problemas

### Error: Docker daemon no está corriendo

```bash
# macOS
open -a Docker

# Linux
sudo systemctl start docker
```

### Error: Puerto 8000 ya en uso

```bash
# Ver qué está usando el puerto
lsof -i :8000

# Cambiar el puerto en docker-compose.yml
ports:
  - "8001:8000"  # Cambiar 8000 por otro puerto
```

### Error: Contenedor no inicia

```bash
# Ver logs detallados
docker-compose logs kronos-api

# Verificar el estado del contenedor
docker-compose ps

# Reconstruir desde cero
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Error: Importación falla

```bash
# Verificar que el código fuente está copiado correctamente
docker-compose exec kronos-api ls -la /app/src

# Verificar Python path
docker-compose exec kronos-api python -c "import sys; print(sys.path)"

# Ejecutar shell en el contenedor para depurar
docker-compose exec kronos-api bash
```

---

## Comandos Útiles

### Ver logs en tiempo real
```bash
docker-compose logs -f kronos-api
```

### Reiniciar el servicio
```bash
docker-compose restart
```

### Detener el servicio
```bash
docker-compose down
```

### Limpiar todo (contenedores, volúmenes, imágenes)
```bash
docker-compose down -v
docker system prune -f
```

### Ejecutar comandos dentro del contenedor
```bash
docker-compose exec kronos-api bash
```

### Reconstruir imagen (forzar sin caché)
```bash
docker-compose build --no-cache
```

---

## Checklist de Verificación

- [ ] Docker está instalado y corriendo
- [ ] Imagen Docker se construyó correctamente
- [ ] Contenedor está corriendo (`docker ps`)
- [ ] Health endpoint responde (`/health`)
- [ ] Root endpoint responde (`/`)
- [ ] Decisions endpoint responde (`/api/v1/decisions`)
- [ ] Documentación Swagger accesible (`/docs`)
- [ ] Logs no muestran errores críticos

---

## Estado Esperado

Una vez completada la verificación, deberías tener:

1. ✅ Contenedor `kronos-api` corriendo
2. ✅ API accesible en `http://localhost:8000`
3. ✅ Todos los endpoints respondiendo correctamente
4. ✅ Documentación Swagger funcional
5. ✅ Sin errores en los logs

---

## Próximos Pasos

Una vez verificado que todo funciona:

1. Implementar proveedores reales (GPS, tráfico, mapas)
2. Agregar tests unitarios e integración
3. Implementar persistencia si es necesaria
4. Agregar logging y monitoreo
5. Configurar CI/CD
