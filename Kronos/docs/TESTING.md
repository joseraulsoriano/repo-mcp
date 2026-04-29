# Testing - Kronos

Guía completa de testing en Kronos.

---

## Estructura de Tests

```
tests/
├── __init__.py
├── conftest.py              # Configuración compartida
├── unit/                    # Tests unitarios
│   ├── test_policies.py
│   └── test_risk_evaluator.py
└── integration/             # Tests de integración
    └── test_api.py
```

---

## Ejecutar Tests

### Todos los Tests

```bash
# Dentro del contenedor
docker-compose exec kronos-api pytest

# O localmente (si tienes pytest instalado)
pytest
```

### Tests con Coverage

```bash
pytest --cov=src/kronos --cov-report=term-missing --cov-report=html
```

### Tests Específicos

```bash
# Solo tests unitarios
pytest tests/unit/

# Solo tests de integración
pytest tests/integration/

# Test específico
pytest tests/unit/test_policies.py

# Test específico por nombre
pytest -k test_green_light_proceed
```

---

## Tests Unitarios

### Tests de Políticas

**Ubicación:** `tests/unit/test_policies.py`

**Prueba:**
- SignalsPolicy: Decisiones con semáforos
- FilteringPolicy: Lógica de filtrado
- TrafficPolicy: Decisiones según tráfico

**Ejemplo:**
```python
def test_green_light_proceed(base_context):
    """Debe permitir avanzar con semáforo en verde."""
    policy = SignalsPolicy()
    decision = policy.evaluate(base_context)
    assert decision.action == DecisionAction.PROCEED
```

### Tests de RiskEvaluator

**Ubicación:** `tests/unit/test_risk_evaluator.py`

**Prueba:**
- Cálculo de riesgo en condiciones normales
- Aumento de riesgo con velocidad alta
- Riesgo con tráfico bloqueado
- Riesgo combinado con múltiples factores

---

## Tests de Integración

### Tests de API

**Ubicación:** `tests/integration/test_api.py`

**Prueba:**
- Endpoints de salud (/health, /)
- Endpoints de decisiones (GET y POST)
- Endpoints de voz
- Validación de respuestas JSON

**Ejemplo:**
```python
def test_get_decision_with_coordinates(client):
    """GET /decisions debe funcionar con coordenadas."""
    response = client.get(
        "/api/v1/decisions",
        params={"lat": 19.0425, "lng": -98.1981, "speed": 13.89},
    )
    assert response.status_code == 200
    assert "decision" in response.json()
```

---

## Fixtures Disponibles

### conftest.py

Fixtures compartidas para todos los tests:

- `sample_position`: Posición de prueba (Centro de Puebla)
- `sample_user`: Usuario de prueba
- `sample_bike`: Moto de prueba
- `sample_motion`: Movimiento de prueba
- `mock_gps_provider`: Proveedor GPS mock
- `mock_traffic_provider`: Proveedor de tráfico mock
- `mock_map_provider`: Proveedor de mapas mock
- `base_context`: ContextSnapshot completo para pruebas

---

## Cobertura de Código

### Ver Coverage

```bash
pytest --cov=src/kronos --cov-report=term-missing
```

**Objetivo:** >70% de cobertura

### Generar Reporte HTML

```bash
pytest --cov=src/kronos --cov-report=html
# Abrir htmlcov/index.html
```

---

## Pruebas Manuales

### Scripts de Prueba

```bash
# Pruebas básicas
bash scripts/test_kronos_simple.sh

# Pruebas de emergencias
bash scripts/test_emergency.sh

# Pruebas de setup inicial
bash scripts/test_setup_inicial.sh
```

---

## Escribir Nuevos Tests

### Test Unitario Ejemplo

```python
import pytest
from kronos.domain.policies.signals_policy import SignalsPolicy

def test_nueva_politica(base_context):
    """Descripción del test."""
    policy = SignalsPolicy()
    decision = policy.evaluate(base_context)
    
    # Assertions
    assert decision.action == DecisionAction.PROCEED
    assert decision.mode == DecisionMode.NORMAL
```

### Test de Integración Ejemplo

```python
def test_nuevo_endpoint(client):
    """Prueba un nuevo endpoint."""
    response = client.get("/api/v1/nuevo-endpoint")
    assert response.status_code == 200
    data = response.json()
    assert "campo" in data
```

---

## Markers

Usar markers para categorizar tests:

```python
@pytest.mark.slow
def test_lento():
    """Test que toma mucho tiempo."""
    pass

@pytest.mark.integration
def test_api():
    """Test de integración."""
    pass
```

**Ejecutar por marker:**
```bash
pytest -m "not slow"  # Excluir tests lentos
pytest -m integration  # Solo tests de integración
```

---

## Troubleshooting

### Tests Fallan

1. Verificar que el servicio esté corriendo:
   ```bash
   docker-compose ps
   ```

2. Ver logs:
   ```bash
   docker-compose logs kronos-api
   ```

3. Ejecutar test con más detalle:
   ```bash
   pytest -v -s test_nombre.py
   ```

### Import Errors

Asegurar que `src/kronos` esté en el PYTHONPATH o usar:
```bash
pytest --pythonpath=src
```
