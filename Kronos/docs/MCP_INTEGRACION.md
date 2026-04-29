# Integración MCP para Fichas Técnicas

Guía sobre cómo usar MCP (Model Context Protocol) para buscar fichas técnicas de motos en línea.

---

## Visión

En lugar de tener todas las fichas técnicas guardadas localmente, Kronos puede usar MCP para buscar información de motos en línea cuando no está en la base de datos local.

---

## Arquitectura MCP

### Estructura Actual

1. **Base de Datos Local** (`BikeSpecsService`):
   - Fichas técnicas de motos comunes en México
   - Búsqueda rápida
   - No requiere conexión a internet

2. **Servicio MCP** (`BikeSpecsMCPService`):
   - Busca en línea cuando no encuentra localmente
   - Usa web search para encontrar fichas técnicas
   - Cachea resultados para evitar búsquedas repetidas

---

## Implementación Futura con MCP

### Usando MCP para Búsqueda Web

```python
# Ejemplo de cómo sería la integración
def search_online_mcp(self, brand: str, model: str) -> Optional[BikeSpecs]:
    """
    Busca especificaciones en línea usando MCP.
    """
    # Query para buscar ficha técnica
    query = f"{brand} {model} ficha técnica especificaciones velocidad máxima aceleración"
    
    # Usar MCP para buscar en web
    # TODO: Integrar con MCP client
    # results = mcp_client.search(query)
    
    # Extraer datos de la búsqueda
    # specs = extract_specs_from_search(results)
    
    return specs
```

---

## Beneficios de MCP

### Ventajas

1. **No necesita mantener base de datos**: Las fichas técnicas se buscan en línea
2. **Siempre actualizado**: Información más reciente que base de datos local
3. **Soporte para más motos**: No limitado a motos pre-guardadas
4. **Flexibilidad**: Puede buscar información adicional (mantenimiento, etc.)

### Desventajas

1. **Requiere conexión a internet**: No funciona offline
2. **Más lento**: Búsqueda web es más lenta que base de datos local
3. **Menos confiable**: Depende de disponibilidad de servicios web

---

## Estrategia Híbrida (Recomendada)

### Mejor Enfoque

1. **Primero**: Buscar en base de datos local (rápido)
2. **Si no encuentra**: Buscar en línea usando MCP (más lento)
3. **Cachear resultado**: Guardar en cache para próximas búsquedas

### Implementación

```python
def search_bike(self, brand: str, model: str) -> Optional[BikeSpecs]:
    # 1. Buscar en base de datos local
    local_result = self.local_service.search_bike(brand, model)
    if local_result:
        return local_result
    
    # 2. Buscar en línea usando MCP
    online_result = self.mcp_service.search_online(brand, model)
    if online_result:
        # 3. Cachear resultado para próximas búsquedas
        self.local_service.cache_specs(brand, model, online_result)
        return online_result
    
    # 3. Crear especificaciones por defecto
    return self._create_default_specs(brand, model)
```

---

## Preparación para MCP

### Servicio Preparado

Ya existe `BikeSpecsMCPService` preparado para integración con MCP:

- **Local primero**: Busca en base de datos local
- **Fallback MCP**: Si no encuentra, busca en línea (estructura lista)
- **Especificaciones por defecto**: Si nada funciona, crea defaults

### Próximos Pasos para Integración Real

1. **Configurar MCP Client**: Integrar cliente MCP en el proyecto
2. **Implementar `search_online()`**: Usar MCP para búsqueda web
3. **Parser de resultados**: Extraer datos de fichas técnicas de resultados web
4. **Cache inteligente**: Guardar resultados encontrados para evitar búsquedas repetidas

---

## Ejemplo de Query MCP

### Búsqueda de Ficha Técnica

```
Query: "Honda CBR 600 ficha técnica especificaciones máxima velocidad aceleración"
```

### Datos a Extraer

- Marca: Honda
- Modelo: CBR 600
- Cilindraje: 600 cc
- Velocidad máxima: ~280 km/h
- Aceleración máxima: ~4.5 m/s²
- Tipo: Sport

---

## Notas

### Estado Actual

- **Base de datos local**: Funcionando con motos comunes
- **Servicio MCP**: Estructura preparada, esperando integración de MCP client
- **Especificaciones por defecto**: Funciona como fallback

### Futuro

Una vez integrado MCP:
- Búsqueda automática en línea cuando no se encuentra localmente
- Cache inteligente de resultados
- Soporte para cualquier moto, no solo las pre-guardadas
