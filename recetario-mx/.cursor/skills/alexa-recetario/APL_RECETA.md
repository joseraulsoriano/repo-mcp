# APL para Recetario MX: voz + pantalla

El backend solo devuelve JSON. Quien debe adaptar la respuesta a **solo voz** o **voz + pantalla** es la **Lambda** de la skill, no el backend.

## Flujo en la Lambda

1. **Todos los dispositivos:** Construir `speakOutput` con el texto que Alexa dira (nombre de receta, descripcion breve, costo). Devolverlo con `responseBuilder.speak(speakOutput)`.
2. **Dispositivos con pantalla:** Ademas, comprobar si el dispositivo soporta APL y, si es asi, anadir la directiva `RenderDocument` con un documento APL que muestre la misma receta (titulo, descripcion, ingredientes, costo).

Asi un Echo Dot solo oye; un Echo Show oye y ve la pantalla.

## Detectar si el dispositivo tiene pantalla

En el handler (Node.js), antes de construir la respuesta:

```javascript
const supportsAPL = handlerInput.requestEnvelope.context.System.device.supportedInterfaces['Alexa.Presentation.APL'];
```

- `supportsAPL === true` -> anadir APL a la respuesta.
- `supportsAPL` ausente o false -> solo voz.

## Documento APL minimo para una receta

El siguiente JSON es un documento APL que muestra titulo, descripcion, ingredientes y costo. La Lambda lo rellena con los datos de la receta que devolvio el backend.

```json
{
  "type": "APL",
  "version": "2023.1",
  "mainTemplate": {
    "parameters": ["payload"],
    "item": {
      "type": "Container",
      "direction": "column",
      "paddingLeft": 24,
      "paddingRight": 24,
      "paddingTop": 24,
      "paddingBottom": 24,
      "items": [
        {
          "type": "Text",
          "text": "${payload.recipeName}",
          "fontSize": 28,
          "fontWeight": "bold",
          "color": "#ea580c"
        },
        {
          "type": "Text",
          "text": "${payload.description}",
          "fontSize": 16,
          "color": "#374151",
          "wrap": true,
          "paddingTop": 12
        },
        {
          "type": "Text",
          "text": "Ingredientes",
          "fontSize": 18,
          "fontWeight": "bold",
          "color": "#ea580c",
          "paddingTop": 16
        },
        {
          "type": "Text",
          "text": "${payload.ingredientsText}",
          "fontSize": 14,
          "color": "#4b5563",
          "wrap": true,
          "paddingTop": 4
        },
        {
          "type": "Text",
          "text": "Costo aprox: $${payload.cost} MXN",
          "fontSize": 14,
          "fontWeight": "bold",
          "color": "#059669",
          "paddingTop": 12
        }
      ]
    }
  }
}
```

`payload` lo envia la Lambda al renderizar el documento (ver abajo).

## En el Lambda: anadir APL a la respuesta (GetRecipeIntentHandler)

Despues de obtener `recetas` del backend y construir `speakOutput`, hacer algo asi:

```javascript
let response = handlerInput.responseBuilder
  .speak(speakOutput)
  .reprompt('¿Quieres otra receta?');

if (handlerInput.requestEnvelope.context.System.device.supportedInterfaces['Alexa.Presentation.APL']) {
  const r = recetas[0];
  const ingredientsText = (r.ingredients && r.ingredients.length)
    ? r.ingredients.map(i => i.name || i).join(', ')
    : 'Ver descripcion';
  response = response.addDirective({
    type: 'Alexa.Presentation.APL.RenderDocument',
    version: '2023.1',
    document: APL_DOCUMENT_RECETA,  // el JSON de arriba como objeto
    datasources: {
      payload: {
        recipeName: r.name,
        description: r.description || '',
        ingredientsText,
        cost: Math.round(r.cost || 0)
      }
    }
  });
}

return response.getResponse();
```

`APL_DOCUMENT_RECETA` es el documento APL de la seccion anterior guardado como constante (objeto JSON) en el Lambda, o cargado desde un archivo.

## Resumen

| Dispositivo   | Que hace la Lambda                                      |
|---------------|---------------------------------------------------------|
| Sin pantalla  | Solo `speak(speakOutput)` + reprompt                   |
| Con pantalla  | `speak(speakOutput)` + `addDirective(RenderDocument)` con el APL de la receta |

El backend no cambia: sigue devolviendo `{ recetas: [ { name, description, cost, ingredients, ... } ] }`. La Lambda usa ese JSON para la voz y para rellenar el APL en dispositivos con pantalla.
