# Comunicación por Voz - Kronos

Guía para usar la funcionalidad de síntesis de voz (Text-to-Speech) de Kronos.

---

## Características

Kronos puede convertir las decisiones del Policy Engine a audio para dar indicaciones por voz al motociclista.

### Funcionalidades

- **Síntesis de voz**: Convierte mensajes de texto a audio MP3
- **Español mexicano**: Configurado para acento mexicano
- **Velocidad ajustable**: Opción de hablar más lento
- **Integración con decisiones**: Audio automático de las decisiones del Policy Engine

---

## Endpoints de Voz

### 1. Audio de Decisión (GET)

Obtiene audio de una decisión basada en coordenadas.

```bash
curl "http://localhost:8000/api/v1/audio?lat=19.0425&lng=-98.1981&speed=13.89&use_osm=true" \
  --output decision.mp3
```

**Parámetros:**
- `lat`: Latitud (opcional)
- `lng`: Longitud (opcional)
- `speed`: Velocidad en m/s (opcional)
- `use_osm`: Usar OpenStreetMap (opcional, default: false)
- `slow`: Hablar más lento (opcional, default: false)

**Respuesta:**
- Audio MP3 con la decisión hablada
- Content-Type: `audio/mpeg`

---

### 2. Audio de Decisión (POST)

Similar a GET pero usando POST.

```bash
curl -X POST "http://localhost:8000/api/v1/audio?slow=true" \
  -H "Content-Type: application/json" \
  --output decision.mp3
```

---

### 3. Texto a Voz (GET)

Convierte cualquier texto a voz.

```bash
curl "http://localhost:8000/api/v1/audio/text?text=No+filtres.+No+ganarás+tiempo&language=es&slow=false" \
  --output voz.mp3
```

**Parámetros:**
- `text`: Texto a convertir (requerido)
- `language`: Código de idioma (opcional, default: es)
- `slow`: Hablar más lento (opcional, default: false)

---

### 4. Texto a Voz (POST)

Similar a GET pero usando POST.

```bash
curl -X POST "http://localhost:8000/api/v1/audio/text?text=Tráfico+fluido.+Puedes+avanzar+normalmente&slow=false" \
  --output voz.mp3
```

---

## Ejemplos de Uso

### Obtener Audio de Decisión desde Puebla

```bash
# Centro de Puebla
curl "http://localhost:8000/api/v1/audio?lat=19.0425&lng=-98.1981&speed=13.89&use_osm=true" \
  --output decision_centro.mp3

# Ángelopolis (más lento para escuchar mejor)
curl "http://localhost:8000/api/v1/audio?lat=19.0500&lng=-98.2267&speed=13.89&use_osm=true&slow=true" \
  --output decision_angelopolis.mp3
```

### Reproducir Audio

**En macOS:**
```bash
# Reproducir inmediatamente
curl "http://localhost:8000/api/v1/audio?lat=19.0425&lng=-98.1981" --output - | afplay -

# Guardar y reproducir
curl "http://localhost:8000/api/v1/audio?lat=19.0425&lng=-98.1981" --output decision.mp3
afplay decision.mp3
```

**En Linux:**
```bash
# Reproducir con mpg123 (requiere instalación)
curl "http://localhost:8000/api/v1/audio?lat=19.0425&lng=-98.1981" --output - | mpg123 -

# O con ffplay
curl "http://localhost:8000/api/v1/audio?lat=19.0425&lng=-98.1981" --output - | ffplay -
```

**En Windows (PowerShell):**
```powershell
# Guardar y reproducir
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/audio?lat=19.0425&lng=-98.1981" -OutFile "decision.mp3"
Start-Process "decision.mp3"
```

---

## Integración en Aplicaciones

### HTML5 Audio

```html
<audio controls>
  <source src="http://localhost:8000/api/v1/audio?lat=19.0425&lng=-98.1981" type="audio/mpeg">
  Tu navegador no soporta audio HTML5.
</audio>
```

### JavaScript/TypeScript

```javascript
// Reproducir audio de decisión
async function playDecision(lat, lng, speed) {
  const audioUrl = `http://localhost:8000/api/v1/audio?lat=${lat}&lng=${lng}&speed=${speed}`;
  const audio = new Audio(audioUrl);
  await audio.play();
}

// Ejemplo de uso
playDecision(19.0425, -98.1981, 13.89);
```

### Python

```python
import requests
import pygame  # o usar playsound, etc.

def play_decision_audio(lat, lng, speed=13.89):
    url = "http://localhost:8000/api/v1/audio"
    params = {"lat": lat, "lng": lng, "speed": speed}
    
    response = requests.get(url, params=params)
    
    # Guardar audio
    with open("decision.mp3", "wb") as f:
        f.write(response.content)
    
    # Reproducir (requiere pygame)
    pygame.mixer.init()
    pygame.mixer.music.load("decision.mp3")
    pygame.mixer.music.play()
```

---

## Configuración de Voz

### Idiomas Soportados

El servicio usa Google Text-to-Speech (gTTS) que soporta múltiples idiomas:

- `es`: Español (default, acento mexicano)
- `en`: Inglés
- `fr`: Francés
- `de`: Alemán
- Y muchos más...

### Acentos Mexicanos

Por defecto está configurado para acento mexicano (`tld="com.mx"`).

Para cambiar el acento, modifica `VoiceConfig` en `src/kronos/infrastructure/services/tts_service.py`.

### Velocidad

- `slow=false`: Velocidad normal (default)
- `slow=true`: Habla más lento (útil en tráfico o para entender mejor)

---

## Mensajes de Voz

### Formato de Mensajes

Los mensajes del Policy Engine se formatean automáticamente para voz:

- Se eliminan caracteres especiales
- Se expanden abreviaciones (km/h → kilómetros por hora)
- Se capitaliza la primera letra
- Se agrega punto final si falta

### Ejemplos de Mensajes

**Decisión normal:**
> "Tráfico fluido. Puedes avanzar normalmente."

**Advertencia:**
> "No filtres. No ganarás tiempo suficiente."

**Precaución:**
> "No puedo evaluar este tramo con precisión. Mantén carril y velocidad."

---

## Limitaciones

### Requiere Conexión a Internet

Google Text-to-Speech requiere conexión a internet para generar audio.

### Rate Limiting

Google TTS puede tener límites de velocidad. Para producción, considera:
- Cachear audios generados
- Usar un servicio TTS dedicado (Azure, AWS Polly)
- Implementar un TTS local (espeak, Festival)

### Calidad de Audio

La calidad es buena pero puede variar según el mensaje. Para mejor calidad:
- Usa servicios de pago (Azure, AWS Polly)
- Implementa TTS neuronal (Tacotron2, FastSpeech)

---

## Próximos Pasos

### Mejoras Futuras

1. **Cache de Audio**: Guardar audios generados para evitar regeneración
2. **TTS Local**: Implementar TTS offline (espeak, pyttsx3)
3. **Múltiples Voces**: Permitir seleccionar voz masculina/femenina
4. **Interrupciones**: Permitir cancelar reproducción
5. **Notificaciones Push**: Integrar con notificaciones del sistema

---

## Troubleshooting

### Error: "No module named 'gtts'"

Instala la dependencia:
```bash
pip install gtts
```

O reconstruye Docker:
```bash
docker-compose build
docker-compose up -d
```

### Audio no se reproduce

Verifica que el archivo MP3 sea válido:
```bash
file decision.mp3
# Debe mostrar: decision.mp3: Audio file with ID3 version
```

### Error de conexión

Google TTS requiere internet. Verifica conectividad:
```bash
curl -I https://translate.google.com
```

---

## Referencias

- [gTTS Documentation](https://gtts.readthedocs.io/)
- [Google Text-to-Speech](https://cloud.google.com/text-to-speech)
- [FastAPI Response Types](https://fastapi.tiangolo.com/advanced/custom-response/)
