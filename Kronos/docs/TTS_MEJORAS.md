# Mejoras de Voz TTS - Kronos

Guía sobre mejoras implementadas y opciones futuras para voz más natural.

---

## Problema Actual

gTTS (Google Text-to-Speech) tiene **limitaciones inherentes**:
- Voces sintéticas que siempre suenan robóticas
- Calidad limitada por diseño
- No hay opción de voces neuronales premium

---

## Mejoras Implementadas

### 1. `slow=True` (Implementado)

**Cambio:** Configuración `slow=True` en lugar de `slow=False`

**Por qué ayuda:**
- gTTS suena menos robótico a velocidad lenta
- Pronunciación más clara
- Menos "cortes" en las palabras

**Configuración:**
```python
VoiceConfig(language="es", slow=True, tld="com.mx")
```

**Resultado:** Mejora moderada, pero sigue sonando robótico

---

## Limitaciones de gTTS

### Por qué sigue sonando robótico

1. **Tecnología antigua**: gTTS usa voces concatenativas, no neuronales
2. **Calidad fija**: No hay opción de mejor calidad
3. **Voces sintéticas**: Todas las voces suenan artificiales

**Conclusión:** gTTS nunca sonará realmente natural, solo menos robótico.

---

## Soluciones Reales (Recomendadas)

### 1. Azure Text-to-Speech (Mejor Opción)

**Ventajas:**
- ✅ Voces neuronales ultra realistas
- ✅ Acentos mexicanos disponibles
- ✅ Calidad profesional
- ✅ Precio razonable

**Ejemplo de voz disponible:**
- **Rosa** (español mexicano, femenina, natural)
- **Francisco** (español mexicano, masculino, natural)

**Implementación:**
```python
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer

speech_config = SpeechConfig(subscription="KEY", region="eastus")
speech_config.speech_synthesis_voice_name = "es-MX-RosaNeural"

synthesizer = SpeechSynthesizer(speech_config=speech_config)
result = synthesizer.speak_text_async("Bienvenido a Kronos").get()
audio = result.audio_data
```

**Costo:** ~$16 por millón de caracteres (muy barato)

---

### 2. AWS Polly

**Ventajas:**
- ✅ Buenas voces en español
- ✅ Integración fácil con AWS
- ✅ Precio competitivo

**Voz recomendada:**
- **Mia** (español mexicano, femenina)

**Costo:** ~$4 por millón de caracteres

---

### 3. ElevenLabs (Premium)

**Ventajas:**
- ✅ Voces ultra realistas
- ✅ Casi indistinguible de humano
- ✅ Control total sobre voz

**Desventajas:**
- ❌ Caro ($5/mes para inicio)
- ❌ Más complejo de integrar

**Mejor para:** Producción final, si el presupuesto lo permite

---

## Implementación Futura

### Estructura Preparada

Ya existe `PremiumTTSService` preparado para integración:

```python
# En tts_service_enhanced.py
class PremiumTTSService:
    """Servicio para Azure, AWS Polly, ElevenLabs."""
    # Estructura lista para implementar
```

### Pasos para Integrar Azure TTS

1. **Instalar SDK:**
```bash
pip install azure-cognitiveservices-speech
```

2. **Configurar API Key:**
```bash
export AZURE_SPEECH_KEY="tu-key"
export AZURE_SPEECH_REGION="eastus"
```

3. **Implementar en PremiumTTSService:**
```python
def text_to_speech(self, text: str, voice_name: str = "es-MX-RosaNeural"):
    # Usar Azure SDK
    ...
```

---

## Comparación de Calidad

| Servicio | Calidad | Naturalidad | Precio | Acentos MX |
|----------|---------|-------------|--------|------------|
| **gTTS** | ⭐⭐ | Robótico | Gratis | Limitado |
| **AWS Polly** | ⭐⭐⭐⭐ | Muy bueno | $4/M chars | Excelente |
| **Azure TTS** | ⭐⭐⭐⭐⭐ | Excelente | $16/M chars | Excelente |
| **ElevenLabs** | ⭐⭐⭐⭐⭐ | Ultra real | $5/mes | Muy bueno |

---

## Recomendación

### Para Desarrollo (Ahora)

Usar **gTTS con `slow=True`**:
- ✅ Gratis
- ✅ Funciona inmediatamente
- ⚠️ Calidad limitada pero aceptable para pruebas

### Para Producción (Futuro)

Migrar a **Azure Text-to-Speech**:
- ✅ Excelente calidad
- ✅ Precio razonable
- ✅ Voces mexicanas naturales
- ✅ Fácil integración

---

## Prueba de Calidad

### Audio Actual (gTTS con slow=True)

```bash
curl "http://localhost:8000/api/v1/welcome/audio" --output welcome_gtts.mp3
afplay welcome_gtts.mp3
```

**Resultado esperado:** Menos robótico, pero aún sintético

### Audio Futuro (Azure TTS)

Una vez implementado Azure TTS, la voz será:
- ✅ Natural y fluida
- ✅ Pronunciación perfecta
- ✅ Acento mexicano auténtico
- ✅ Indistinguible de humano (casi)

---

## Pasos Siguientes

1. **Prueba gTTS mejorado:** Ya está implementado con `slow=True`
2. **Si no es suficiente:** Configurar Azure TTS (requiere API key)
3. **Implementar PremiumTTSService:** Usar Azure SDK
4. **Migrar gradualmente:** Cambiar de gTTS a Azure en producción

---

## Notas Técnicas

### Por qué `slow=True` ayuda

- **Mejor prosodia:** Pausas más naturales
- **Menos cortes:** Palabras menos "cortadas"
- **Claridad:** Pronunciación más clara

### Por qué gTTS nunca será perfecto

- **Tecnología antigua:** Concatenación de fonemas, no redes neuronales
- **Sin entrenamiento reciente:** Modelos viejos
- **Diseño simple:** No está optimizado para naturalidad

---

## Conclusión

**Para ahora:**
- Usar gTTS con `slow=True` (ya implementado)
- Calidad mejor pero limitada

**Para producción:**
- Migrar a Azure TTS para voz realmente natural
- Inversión mínima, ganancia máxima en calidad
