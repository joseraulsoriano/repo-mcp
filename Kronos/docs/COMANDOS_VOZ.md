# Comandos de Voz - Kronos

Guía para usar comandos de voz en Kronos.

---

## Funcionalidad

Kronos ahora puede procesar comandos de voz para navegar a destinos:

- **"Kronos vamos a trabajo"**
- **"Kronos vamos a casa"**
- **"vamos a centro"**
- **"ir a universidad"**

---

## Endpoints

### 1. Procesar Comando de Voz (Texto)

**POST** `/api/v1/voice/command/text`

Procesa un comando de voz después de convertir audio a texto (STT).

```bash
curl -X POST "http://localhost:8000/api/v1/voice/command/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Kronos vamos a trabajo",
    "user_id": "user-id-optional"
  }'
```

**Respuesta:**
```json
{
    "action": "navigate",
    "destination": "trabajo",
    "destination_coords": {
        "lat": 19.0500,
        "lng": -98.2267
    },
    "message": "Entendido. Vamos a trabajo.",
    "success": true
}
```

---

### 2. Procesar Comando de Voz (Audio)

**POST** `/api/v1/voice/command`

Procesa un comando desde archivo de audio.

**Nota:** Por ahora, STT desde audio requiere implementación adicional (Whisper, Google STT, etc.).

```bash
curl -X POST "http://localhost:8000/api/v1/voice/command" \
  -F "audio=@comando.wav" \
  -F "user_id=user-id-optional"
```

---

### 3. Probar Comando (GET)

**GET** `/api/v1/voice/command/test`

Prueba rápida de un comando de voz.

```bash
curl "http://localhost:8000/api/v1/voice/command/test?text=Kronos vamos a trabajo&user_id=optional"
```

---

## Destinos Reconocidos

### Destinos Estándar

- **trabajo** / oficina / office
- **casa** / hogar / home
- **universidad** / uni / escuela
- **centro** / centro histórico / zócalo
- **angelopolis** / ángel / plaza ángel
- **cholula** / san pedro cholula

### Destinos Personalizados

Si el usuario tiene destinos frecuentes guardados en su perfil, el sistema los reconoce automáticamente.

---

## Flujo Completo

### 1. Usuario dice comando

```
"Kronos vamos a trabajo"
```

### 2. STT convierte audio a texto

```
text: "Kronos vamos a trabajo"
```

### 3. Procesar comando

```bash
curl -X POST "http://localhost:8000/api/v1/voice/command/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "Kronos vamos a trabajo", "user_id": "tu-user-id"}'
```

### 4. Sistema busca destino

- Busca en destinos frecuentes del usuario
- Si encuentra, retorna coordenadas
- Si no encuentra, solicita coordenadas

### 5. Configurar ruta

Una vez que se tiene el destino, se puede usar para decisiones:

```bash
curl "http://localhost:8000/api/v1/decisions?lat=19.0425&lng=-98.1981&user_id=tu-user-id"
```

---

## Mejora de Voz TTS

### Cambios Implementados

1. **Acento mexicano**: Cambiado de español de España a mexicano para sonar más natural
2. **Velocidad normal**: Mantiene velocidad natural (no lenta) para sonar menos robótica

### Limitaciones de gTTS

gTTS usa voces sintéticas que pueden sonar robóticas. Para mejor calidad:

**Opciones futuras:**
- **Azure Text-to-Speech**: Voces neuronales muy naturales
- **AWS Polly**: Buena calidad, acentos mexicanos
- **ElevenLabs**: Voces ultra realistas (de pago)
- **Whisper TTS**: Modelos locales de alta calidad

---

## Script de Prueba

```bash
# Ejecutar todas las pruebas de comandos de voz
bash scripts/test_voice_command.sh
```

---

## Ejemplos de Uso

### Comando Básico

```bash
curl -X POST "http://localhost:8000/api/v1/voice/command/text" \
  -H "Content-Type: application/json" \
  -d '{"text": "Kronos vamos a trabajo"}'
```

### Con User ID (usa destinos frecuentes)

```bash
USER_ID="tu-user-id"
curl -X POST "http://localhost:8000/api/v1/voice/command/text" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Kronos vamos a trabajo\", \"user_id\": \"$USER_ID\"}"
```

### Prueba Rápida

```bash
curl "http://localhost:8000/api/v1/voice/command/test?text=Kronos vamos a casa"
```

---

## Integración Futura con STT Real

### Whisper (Recomendado)

Para procesar audio directamente:

```python
import whisper

model = whisper.load_model("base")
result = model.transcribe("audio.wav")
text = result["text"]
```

### Google Speech-to-Text

```python
from google.cloud import speech

client = speech.SpeechClient()
# Configurar y procesar audio
```

---

## Próximos Pasos

1. **STT Real**: Integrar Whisper o servicio STT para procesar audio directamente
2. **Geocodificación**: Integrar Nominatim para buscar direcciones por nombre
3. **Confirmación de Voz**: Reproducir confirmación con destino encontrado
4. **Mejor TTS**: Migrar a Azure TTS o AWS Polly para voces más naturales
