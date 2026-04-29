---
name: alexa-recetario
description: Desarrolla y mantiene la Skill de Alexa del Recetario MX (recetas mexicanas). Usa cuando se trabaje en la Skill de Alexa para recetas, con pantalla (APL) o solo voz, o cuando se integre el MCP/API del recetario con Alexa.
---

# Alexa Skill - Recetario MX

Skill de Alexa que expone el Recetario MX (recetario-mx): recetas mexicanas, sugerencias por ingredientes y presupuesto, con soporte para dispositivos con pantalla y solo voz.

## Origen de datos: MCP / API

Backend en Next.js, directorio `src/app/api/mcp/`:

| Endpoint | Método | Uso en Alexa |
|----------|--------|--------------|
| `/api/mcp/recipes` | POST | Generar recetas por tipo de comida, presupuesto, gustos/disgustos |
| `/api/mcp/suggestions` | POST | Menú completo (desayuno, comida, cena) para un usuario |
| `/api/mcp/ingredients` | GET | Listar ingredientes (por usuario si aplica) |
| `/api/mcp/prices` | GET | Precios de ingredientes |

**Body típico para recetas** (`/api/mcp/recipes`):

- `ingredientes`: array de objetos con `name`, `price`, `category`, `nutritionalInfo`
- `presupuestoDiario`: number
- `gustos`: string[]
- `disgustos`: string[]
- `objetivo`: "ahorrar" | "saludable"
- `tipoComida`: "desayuno" | "comida" | "cena"

**Respuesta**: `{ recetas: Array<{ name, ingredients, cost, calories, description }> }`

**Body para sugerencias** (`/api/mcp/suggestions`):

- `userId`, `presupuesto`, `gustos`, `disgustos`, `objetivo`, `tiposComida` (array)

**Respuesta**: `{ menu: Record<string, Recipe[]> }` (ej. `menu.desayuno`, `menu.comida`, `menu.cena`).

## Diseño de la Skill: con y sin pantalla

- **Solo voz**: respuestas breves, listas cortas (2–3 ítems), opción de “siguiente” o “repetir”. No asumir que el usuario ve nada.
- **Con pantalla (APL)**: además del habla, enviar documento APL con título de receta, ingredientes, pasos y (opcional) imagen. Mantener coherencia entre lo que Alexa dice y lo que se muestra.

Implementar handlers que comprueben `context.System.device.supportedInterfaces['Alexa.Presentation.APL']` para decidir si enviar directiva APL o solo respuesta de voz.

## Invocation y nombre de la Skill

- **Skill name** (en Developer Console): nombre interno, máx. 50 caracteres. Ejemplo: "Recetario MX" o "Mexican Recipe Helper".
- **Invocation name**: lo que el usuario dice para abrir la skill ("Alexa, abre Recetario MX"). Debe coincidir con el locale (es-MX vs en-US).

## Locales

- **es-MX**: principal para Recetario MX (recetas mexicanas, audiencia México).
- **en-US**: opcional para expansión; mantener mismos intents y slots, solo cambiar prompts y respuestas.

Al añadir locale, duplicar/interpolar recursos de idioma (prompts, APL textos) y probar en ambos.

## Estructura recomendada del proyecto Alexa

- `lambda/` o código del backend (Node.js/Python) que llama a la API del recetario (`NEXT_PUBLIC_APP_URL` o variable de entorno).
- Modelo de interacción: intents para "pedir receta", "recetas por ingredientes", "menú del día", "siguiente paso", "repetir", "ayuda", "cancelar/salir".
- Slots: tipo de comida, ingredientes, número de porciones (opcional).
- Respuestas: SSML cuando ayude (pausas, énfasis); en pantalla, listas y textos cortos.

## Referencias en el repo

- API MCP: `src/app/api/mcp/recipes/route.ts`, `suggestions/route.ts`, `ingredients/route.ts`, `prices/route.ts`
- Modelo de datos: `prisma/schema.prisma` (Recipe, Ingredient, User, MealPlan)
- Configuración Alexa: ver `ALEXA_SETUP.md` en la raíz del proyecto (nombre de skill, locale, testing).
