# Configuracion de la Skill en Alexa Developer Console

Respuestas directas para el formulario de creacion de la Skill (nombre, locale e instrucciones de prueba).

---

## 1. Skill name (nombre de la Skill)

**Campo:** Skill name (0/50 caracteres)

**Opciones recomendadas:**

| Nombre | Caracteres | Nota |
|--------|------------|------|
| Recetario MX | 12 | Nombre del proyecto; uso referencial si no es marca registrada |
| Mexican Recipe Helper | 23 | Generico, sin marca |
| Recetas Mexicanas | 18 | En espanol |
| My Mexican Recipes | 20 | En ingles |

**Sugerencia:** Si "Recetario MX" es el nombre de tu app y no una marca de terceros, puedes usarlo. Si quieres evitar cualquier revision de marca, usa **Mexican Recipe Helper** o **Recetas Mexicanas**.

---

## 2. Primary locale (idioma principal)

**Campo:** Choose a primary locale

- **Spanish (Mexico) – es-MX**: Recomendado para Recetario MX (recetas mexicanas, audiencia en Mexico). Coincide con el contenido y el dominio del proyecto.
- **English (US) – en-US**: Usar si la Skill se lanzara primero en Estados Unidos o quieres priorizar ingles. Puedes anadir es-MX despues en "Add locale".

**Recomendacion:** Para "recetario-mx", usar **Spanish (Mexico)** como primary locale y anadir **English (US)** despues si aplica.

---

## 3. Testing instructions (cuando te lo pidan)

Incluir algo como:

- La Skill ofrece recetas mexicanas y sugerencias de menu segun ingredientes y presupuesto.
- Funciona en dispositivos con pantalla (APL) y solo voz.
- Para probar: "Alexa, abre [invocation name]" y pedir una receta o menu del dia.
- No implica uso de marcas de terceros; "Recetario MX" es el nombre del producto/servicio propio.

---

## 4. Choose a type of experience

**Campo:** Tell us what kind of experience you want to build

**Seleccion:** **Food & Drink**

Es la categoria correcta para Recetario MX: recetas, ingredientes, menu, comida y bebida. Alexa usara un modelo de interaccion orientado a este tipo de skill.

---

## 5. Choose a model

**Campo:** Based on what you've told us, we think this model would work best

**Seleccion:** **Custom**

- Permite definir todos los intents y slots (receta, ingredientes, tipo de comida, presupuesto, etc.).
- Incluye interacciones de voz basicas (parar, cancelar, ayuda, ir a inicio).
- Permite respuestas visuales con APL (dispositivos con pantalla) y audio/SSML.
- Se adapta al flujo del Recetario MX (llamadas a tu API MCP).

**Sync Locales:** Opcional. Si activas "Sync Locales", los cambios del modelo se propagan a todos los locales del mismo idioma. Puedes activarlo o desactivarlo luego en language settings.

---

## 6. Hosting services

**Campo:** Provision your own backend or Alexa can host

**Opciones:**

| Opcion | Cuando usarla |
|--------|----------------|
| **Alexa-hosted (Node.js)** | Recomendado para empezar. Lambda gratuito, editor en consola, despliegue rapido. El Lambda solo debe llamar a tu API de recetario-mx (Next.js). |
| **Alexa-hosted (Python)** | Igual que Node.js pero en Python. Elige si prefieres escribir el handler en Python. |
| **Provision your own** | Si quieres tu propia Lambda en tu cuenta AWS, sin limites del tier Alexa-hosted, o integrar con otros recursos. Requiere cuenta AWS y despliegue manual. |

**Recomendacion:** **Alexa-hosted (Node.js)** para arrancar: el backend real ya esta en recetario-mx (Next.js); el Lambda solo recibe la peticion de Alexa, llama a `POST /api/mcp/recipes` o `/api/mcp/suggestions` y devuelve la respuesta. Si mas adelante superas limites (S3, Dynamo, etc.), puedes migrar a "Provision your own".

---

## Resumen para copiar/pegar

- **Skill name:** Recetario MX *(o Mexican Recipe Helper si prefieres evitar marca)*
- **Primary locale:** Spanish (Mexico) *(o English (US) si priorizas en-US)*
- **Type of experience:** Food & Drink
- **Model:** Custom
- **Hosting:** Alexa-hosted (Node.js) *(recomendado para empezar)*

El Cursor Skill `.cursor/skills/alexa-recetario/SKILL.md` documenta la API MCP, el diseno con/sin pantalla y la estructura recomendada para la Skill.

---

## 7. Backend Node.js para la Skill (modular, MCP)

En **`backend-alexa/`** hay un backend Node.js **modular** (no monolito) que apunta al mismo contrato que el MCP de recetario-mx:

- **Secciones:** recetas (`/api/mcp/recipes`), ingredientes (`/api/mcp/ingredients`), sugerencias/menu (`/api/mcp/suggestions`), precios/compras (`/api/mcp/prices`), salud (`/health`).
- **Estructura:** `server.js` (entrada y enrutador), `lib/` (response, parseBody), `routes/` (una ruta por seccion), `data/` (datos demo por dominio). Sin dependencias externas.

**Levantar el backend:**

```bash
cd recetario-mx/backend-alexa
node server.js
```

Servidor en **http://localhost:3001**. Para que la Skill (Lambda) lo use:

1. **Probar en local:** usa **ngrok** (`ngrok http 3001`) y en la Skill (Lambda) define `API_RECETARIO_URL` = `https://TU-URL-NGROK.ngrok.io/api/mcp/recipes`.
2. **Desplegar:** sube `backend-alexa` a Railway, Render, Fly.io, etc., y pon esa URL + `/api/mcp/recipes` (y el resto de rutas) en las variables de la skill.

Ver `backend-alexa/README.md` para arquitectura y contratos MCP.

---

## 8. Voz y pantalla (ambos tipos de dispositivo)

El backend solo devuelve JSON. La **Lambda** de la skill debe:

- **Todos los dispositivos:** responder con voz (`speakOutput`) usando los datos del backend.
- **Dispositivos con pantalla (Echo Show, etc.):** ademas, comprobar si el dispositivo soporta APL (`context.System.device.supportedInterfaces['Alexa.Presentation.APL']`) y, si es asi, anadir la directiva `RenderDocument` con un documento APL que muestre la receta (titulo, descripcion, ingredientes, costo).

Asi un Echo Dot solo oye; un Echo Show oye y ve la pantalla. El backend no cambia.

Ver `.cursor/skills/alexa-recetario/APL_RECETA.md` para el flujo en la Lambda, el documento APL minimo y el codigo de ejemplo. El JSON del documento esta en `.cursor/skills/alexa-recetario/apl-receta.json`.
