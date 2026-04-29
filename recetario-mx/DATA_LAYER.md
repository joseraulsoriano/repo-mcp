# Capa de datos: DynamoDB y curación para Alexa

La información que devuelve el MCP (Brave + scraping) es **información cruda**: titulos, snippets, URLs. Para Alexa conviene **datos curados**: respuestas breves, estructuradas y reutilizables. Este documento propone usar **DynamoDB** en el ecosistema Alexa como almacen y base para un "data warehouse" ligero que permita curar y elegir las mejores respuestas.

---

## Por qué curar

| Ahora (crudo) | Objetivo (curado) |
|---------------|-------------------|
| Titulos largos, snippets variables | Nombre corto + descripcion pensada para voz |
| Sin ingredientes ni coste normalizado | Ingredientes y coste estimado por receta |
| Misma busqueda puede dar resultados distintos | Respuestas estables y seleccionadas |
| Sin historico ni metricas | Historial y uso para elegir "mejores" |

---

## DynamoDB en Alexa

En **Alexa-hosted**, la skill puede usar **DynamoDB** asociado a la cuenta de desarrollo:

- Crear tablas desde la consola de Alexa (Build > Endpoint > AWS Resources) o desde AWS Console.
- El Lambda de la skill tiene permisos para leer/escribir en esas tablas.
- No hace falta configurar credenciales a mano; el rol de la skill ya incluye acceso.

Flujo propuesto:

1. **Lambda** recibe el intent (ej. GetRecipe).
2. Lambda llama a **backend-alexa** (o directamente a recetario-mcp) y obtiene resultados crudos.
3. Lambda **guarda en DynamoDB** (cache o tabla de "raw") opcional.
4. Lambda **consulta DynamoDB** (tablas curadas): si hay receta/ingrediente/precio curado para ese contexto, lo usa; si no, usa lo crudo o cache.
5. Lambda responde a Alexa con texto/APL.

---

## Esquema de tablas propuesto

### 1. Cache de resultados crudos (opcional)

Para no repetir llamadas al MCP y poder curar despues.

| Tabla | Partition key | Sort key | Uso |
|-------|---------------|----------|-----|
| `RecetarioMCPCache` | `pk` (ej. "RECETAS#desayuno") | `sk` (timestamp o id) | Guardar JSON de recetas devueltas por el MCP por tipoComida/query. TTL para expiracion. |

Atributos ejemplo: `query`, `tipoComida`, `results` (lista), `createdAt`, `ttl`.

### 2. Datos curados (lo que Alexa lee primero)

| Tabla | Partition key | Sort key | Uso |
|-------|---------------|----------|-----|
| `RecetasCurated` | `tipoComida` (desayuno, comida, cena) | `recetaId` (uuid) | Recetas curadas: nombre corto, descripcion voz, ingredientes, coste estimado, urlOrigen. |
| `IngredientesCurated` | `category` (opcional) | `ingredienteId` | Ingredientes curados con nombre, unidad, precio ref. |
| `PreciosCurated` | `productKey` (ej. "arroz") | `store` o `precioId` | Precios curados por producto y tienda. |

Atributos ejemplo para `RecetasCurated`:

- `nombre`, `descripcionVoz`, `ingredientes[]`, `costeEstimado`, `urlOrigen`, `calorias` (opcional), `updatedAt`.

### 3. Warehouse ligero: metricas y "mejores"

Para "procesar las mejores respuestas" sin montar un DWH completo:

| Tabla | Partition key | Sort key | Uso |
|-------|---------------|----------|-----|
| `RecetarioUsage` | `entityType` (RECETA, INGREDIENTE, PRECIO) | `entityId` + `date` (YYYY-MM-DD) | Contador de veces que Alexa uso una receta/ingrediente en una respuesta (por sesion o por usuario). |
| `RecetarioFeedback` | `entityType#entityId` | `timestamp` | Feedback explicito (opcional): "esta receta me gusto" / thumbs up. |

Con eso puedes:

- Consultar las recetas mas usadas por `tipoComida`.
- Promover de cache a curado las mas usadas o con mejor feedback.
- Exportar a S3 (CSV/Parquet) y usar Athena para informes si mas adelante lo necesitas.

---

## Flujo en Lambda (resumen)

```
Usuario: "Alexa, dame una receta de desayuno"
  -> GetRecipeIntent (slot: tipoComida = desayuno)
  -> Lambda:
      1. (Opcional) Leer RecetasCurated donde tipoComida = desayuno; si hay N items, elegir uno (aleatorio o por uso).
      2. Si no hay curados: llamar backend-alexa /api/mcp/recipes { tipoComida: "desayuno" }.
      3. (Opcional) Escribir respuesta cruda en RecetarioMCPCache.
      4. Elegir una receta (curada o del paso 2), formatear para SSML/APL.
      5. (Opcional) Incrementar RecetarioUsage para esa receta.
      6. Responder con speak() y/o APL.
```

---

## Single-table: usar la unica tabla de la skill (solo "Crear elemento")

Si solo puedes **crear elementos** e **indices** en la tabla existente (clave de particion `id`, tipo Cadena), usa un **diseño single-table**: cada tipo de dato tiene un `id` distinto. Todo va en la misma tabla.

### Convencion de `id`

| Prefijo | Ejemplo de `id` | Contenido (atributos del elemento) |
|---------|------------------|-------------------------------------|
| Recetas curadas por tipo | `RECETA#desayuno`, `RECETA#comida`, `RECETA#cena` | `recetas` (Lista), `updatedAt` (Numero) |
| Cache MCP (opcional) | `CACHE#RECETAS#desayuno#1738437120` | `query`, `tipoComida`, `results` (Lista o String JSON), `createdAt`, `ttl` |
| Ingredientes por categoria | `INGREDIENTE#VERDURAS`, `INGREDIENTE#GENERAL` | `items` (Lista de objetos) |
| Precios por producto | `PRECIO#arroz`, `PRECIO#leche` | `items` (Lista: store, name, price, unit) |
| Uso (metricas) | `USAGE#RECETA#rec-001#2026-02-01` | `count` (Numero) |
| Feedback (opcional) | `FEEDBACK#RECETA#rec-001#1738437120000` | `rating` (Numero) |

Un solo elemento por `id`. Para "todas las recetas de desayuno" guardas **un** elemento con `id = RECETA#desayuno` y dentro el atributo `recetas` (lista de recetas). Asi el Lambda hace un solo **GetItem** por tipo de comida.

---

### Crear elemento: recetas curadas (desayuno)

En la tabla, **Crear elemento** y rellena:

**Vista JSON** (recomendado: pega esto y ajusta):

```json
{
  "id": "RECETA#desayuno",
  "recetas": [
    {
      "recetaId": "rec-001",
      "nombre": "Huevos a la mexicana",
      "descripcionVoz": "Huevos revueltos con jitomate, cebolla y chile. Ideal para desayuno.",
      "ingredientes": ["Huevo", "Jitomate", "Cebolla", "Chile verde"],
      "costeEstimado": 25,
      "urlOrigen": "https://www.cocinafacil.com.mx/recetas/huevos-a-la-mexicana"
    },
    {
      "recetaId": "rec-002",
      "nombre": "Chilaquiles verdes",
      "descripcionVoz": "Totopos con salsa verde, crema y queso. Clasico del desayuno mexicano.",
      "ingredientes": ["Tortilla", "Tomate verde", "Crema", "Queso"],
      "costeEstimado": 45,
      "urlOrigen": "https://www.cocinafacil.com.mx/recetas/chilaquiles"
    }
  ],
  "updatedAt": 1738437120
}
```

**Formulario** (si no usas JSON):

| Nombre de atributo | Valor | Tipo |
|--------------------|--------|------|
| id | `RECETA#desayuno` | Cadena |
| updatedAt | `1738437120` | Numero |

Para `recetas` (lista de mapas) en formulario: agrega atributo `recetas`, tipo **Lista**, y dentro añade los mapas (cada receta). Si la consola no deja listas complejas facil, usa **Vista JSON** y pega el JSON de arriba.

---

### Mas elementos de ejemplo (Vista JSON)

**RECETA#comida**

```json
{
  "id": "RECETA#comida",
  "recetas": [
    {
      "recetaId": "rec-c01",
      "nombre": "Arroz con pollo",
      "descripcionVoz": "Pollo guisado con arroz y verduras. Plato completo y economico.",
      "ingredientes": ["Pollo", "Arroz", "Jitomate", "Cebolla"],
      "costeEstimado": 55,
      "urlOrigen": "https://www.cocinafacil.com.mx/recetas/arroz-pollo"
    }
  ],
  "updatedAt": 1738437120
}
```

**RECETA#cena**

```json
{
  "id": "RECETA#cena",
  "recetas": [
    {
      "recetaId": "rec-d01",
      "nombre": "Sopa de tortilla",
      "descripcionVoz": "Caldo de jitomate con tiras de tortilla, aguacate y queso.",
      "ingredientes": ["Tortilla", "Jitomate", "Aguacate", "Queso"],
      "costeEstimado": 35,
      "urlOrigen": "https://www.cocinafacil.com.mx/recetas/sopa-tortilla"
    }
  ],
  "updatedAt": 1738437120
}
```

**INGREDIENTE#GENERAL** (lista simple)

```json
{
  "id": "INGREDIENTE#GENERAL",
  "items": [
    { "ingredienteId": "ing-001", "nombre": "Jitomate", "unit": "kg", "price": 25 },
    { "ingredienteId": "ing-002", "nombre": "Cebolla", "unit": "kg", "price": 20 }
  ]
}
```

**PRECIO#arroz**

```json
{
  "id": "PRECIO#arroz",
  "items": [
    { "store": "Walmart", "name": "Arroz Verde Valle 2 kg", "price": 45, "unit": "kg" }
  ]
}
```

**USAGE** (una vez que el Lambda empiece a registrar)

```json
{
  "id": "USAGE#RECETA#rec-001#2026-02-01",
  "count": 1
}
```

---

### Nombre de la tabla en el Lambda

La tabla que usa la skill suele tener un nombre tipo UUID (ej. `81b9cafb-0b99-42e9-803e-918ad6c60ab2`). En el Lambda necesitas ese nombre para GetItem/PutItem. Lo puedes:

- Sacar de **Build > Endpoint > AWS Resources** en la consola de la skill (recurso DynamoDB), o
- Ponerlo en una variable de entorno del Lambda (ej. `RECETARIO_TABLE`) y leerla en el codigo.

---

### Codigo Lambda: leer RecetasCurated (single-table)

La tabla tiene solo clave de particion `id`. Nombre de tabla: el que aparece en tu skill (Build > Endpoint > AWS Resources), o ponlo en variable de entorno `RECETARIO_TABLE`.

En el Lambda, al inicio del archivo (junto a `const Alexa = require('ask-sdk-core');`):

```javascript
const AWS = require('aws-sdk');
const dynamo = new AWS.DynamoDB.DocumentClient();
const TABLE_NAME = process.env.RECETARIO_TABLE || 'TU_TABLA_UUID'; // reemplaza por el nombre real
```

Funcion auxiliar para leer recetas curadas por tipo de comida:

```javascript
function getRecetasCurated(tipoComida) {
  const id = `RECETA#${tipoComida}`;
  return dynamo.get({
    TableName: TABLE_NAME,
    Key: { id }
  }).promise().then(res => {
    const list = (res.Item && res.Item.recetas) || [];
    return list.length > 0 ? list : null;
  }).catch(() => null);
}
```

En **GetRecipeIntentHandler**, antes de llamar a la API, intenta leer de DynamoDB:

```javascript
// Dentro de handle(handlerInput), despues de obtener validMeal:
const recetasCurated = await getRecetasCurated(validMeal);
if (recetasCurated && recetasCurated.length > 0) {
  const r = recetasCurated[Math.floor(Math.random() * recetasCurated.length)];
  const speakOutput = `Te recomiendo: ${r.nombre}. ${r.descripcionVoz || ''} ${r.costeEstimado ? `Costo aproximado: ${Math.round(r.costeEstimado)} pesos.` : ''} ¿Quieres otra receta?`;
  return resolve(handlerInput.responseBuilder
    .speak(speakOutput)
    .reprompt('¿Quieres otra receta?')
    .getResponse());
}
// Si no hay curados, sigue con la llamada https a API_RECETARIO_URL como ya tienes...
```

Para que `await` funcione, el `handle` debe ser `async handle(handlerInput)` y usar `await getRecetasCurated(validMeal)`.

Si tu skill no tiene el paquete `aws-sdk`: en Alexa-hosted (Node.js) suele venir incluido. Si usas Node 18+ y solo tienes SDK v3, se usaria `@aws-sdk/client-dynamodb` y `DynamoDBDocumentClient`; la logica (GetItem con Key `{ id: 'RECETA#desayuno' }`) es la misma.

---

## Guia paso a paso: crear tablas en la consola DynamoDB (AWS)

La opcion **"Crear tabla"** no esta en el menu **Acciones** de una tabla existente. Hay que ir a la lista de tablas:

1. En el panel izquierdo, asegurate de estar en **Tablas** (Tables).
2. Arriba del listado de tablas suele haber un boton **"Crear tabla"** (Create table). Si no lo ves, haz clic en el nombre del servicio DynamoDB en la parte superior para volver al inicio de DynamoDB y ahi aparece.
3. Para cada tabla nueva, rellena los campos segun la tabla de abajo y luego **"Crear tabla"**.

---

### Tabla 1: RecetarioMCPCache (cache de resultados crudos del MCP)

| Campo | Valor |
|-------|--------|
| Nombre de tabla | `RecetarioMCPCache` |
| Clave de particion | Nombre: `pk`, Tipo: Cadena (String) |
| Clave de ordenacion | Nombre: `sk`, Tipo: Cadena (String) |
| Configuracion de tabla | Modo de capacidad: aprovisionada (o bajo demanda si prefieres). Aprovisionada: 5 unidades de lectura y 5 de escritura minimo para empezar. |
| Configuracion adicional (opcional) | Activar TTL: atributo TTL = `ttl` (numero; epoch en segundos). Lo activas despues de crear la tabla: pestaña "Configuracion" > "Activar TTL". |

Crear tabla. Luego, en la tabla creada: pestaña **Configuracion** > **Editar** en "Configuracion adicional" (o "Activar TTL") y definir el atributo TTL = `ttl`.

---

### Tabla 2: RecetasCurated (recetas curadas para Alexa)

| Campo | Valor |
|-------|--------|
| Nombre de tabla | `RecetasCurated` |
| Clave de particion | Nombre: `tipoComida`, Tipo: Cadena (String) |
| Clave de ordenacion | Nombre: `recetaId`, Tipo: Cadena (String) |
| Configuracion de tabla | Igual que arriba (aprovisionada 5/5 o bajo demanda). |

Sin TTL. Los atributos extra (nombre, descripcionVoz, ingredientes, costeEstimado, urlOrigen, etc.) se anaden al crear o editar elementos, no en la creacion de la tabla.

---

### Tabla 3: IngredientesCurated

| Campo | Valor |
|-------|--------|
| Nombre de tabla | `IngredientesCurated` |
| Clave de particion | Nombre: `category`, Tipo: Cadena (String) |
| Clave de ordenacion | Nombre: `ingredienteId`, Tipo: Cadena (String) |
| Configuracion de tabla | Aprovisionada 5/5 o bajo demanda. |

---

### Tabla 4: PreciosCurated

| Campo | Valor |
|-------|--------|
| Nombre de tabla | `PreciosCurated` |
| Clave de particion | Nombre: `productKey`, Tipo: Cadena (String) |
| Clave de ordenacion | Nombre: `store`, Tipo: Cadena (String) |
| Configuracion de tabla | Aprovisionada 5/5 o bajo demanda. |

---

### Tabla 5: RecetarioUsage (metricas de uso)

| Campo | Valor |
|-------|--------|
| Nombre de tabla | `RecetarioUsage` |
| Clave de particion | Nombre: `entityType`, Tipo: Cadena (String) — valores: RECETA, INGREDIENTE, PRECIO |
| Clave de ordenacion | Nombre: `entityIdDate`, Tipo: Cadena (String) — ej. `recetaId#2026-02-01` |
| Configuracion de tabla | Aprovisionada 5/5 o bajo demanda. |

---

### Tabla 6 (opcional): RecetarioFeedback

| Campo | Valor |
|-------|--------|
| Nombre de tabla | `RecetarioFeedback` |
| Clave de particion | Nombre: `entityKey`, Tipo: Cadena (String) — ej. `RECETA#recetaId` |
| Clave de ordenacion | Nombre: `timestamp`, Tipo: Numero (Number) — epoch en ms |
| Configuracion de tabla | Aprovisionada 5/5 o bajo demanda. |

---

### Resumen de claves

| Tabla | Clave de particion (PK) | Clave de ordenacion (SK) | TTL |
|-------|------------------------|---------------------------|-----|
| RecetarioMCPCache | pk (String) | sk (String) | ttl |
| RecetasCurated | tipoComida (String) | recetaId (String) | — |
| IngredientesCurated | category (String) | ingredienteId (String) | — |
| PreciosCurated | productKey (String) | store (String) | — |
| RecetarioUsage | entityType (String) | entityIdDate (String) | — |
| RecetarioFeedback | entityKey (String) | timestamp (Number) | — |

---

### Despues de crear las tablas

- **Permisos**: El rol del Lambda de la skill Alexa-hosted debe poder acceder a estas tablas. Si las creaste en la misma cuenta/region que la skill, anade en la politica IAM del rol del Lambda los ARN de cada tabla y las acciones: `GetItem`, `PutItem`, `Query`, `UpdateItem`, `BatchGetItem`, `BatchWriteItem`.
- **TTL en RecetarioMCPCache**: En la tabla > pestaña **Configuracion** > buscas "Time to Live (TTL)" > **Activar TTL** y pones el nombre del atributo: `ttl`.

---

## Creacion de tablas en AWS (referencia)

Puedes crearlas desde **AWS Console** (DynamoDB) como arriba, o con **CloudFormation/Terraform** si lo automatizas.

El **rol del Lambda** de la skill debe tener politicas que permitan `dynamodb:GetItem`, `PutItem`, `Query`, `UpdateItem`, `BatchGetItem`, `BatchWriteItem` en estas tablas (por ARN de recurso).

---

## Curación: quien escribe en las tablas curadas

Opciones:

1. **Manual**: desde un panel (Next.js o script) que lea cache o resultados crudos y permita "aprobar" y guardar en RecetasCurated con nombre/descripcion/ingredientes editados.
2. **Semiatomático**: un job (Lambda programada o script local) que lea RecetarioMCPCache o llame al MCP, filtre por dominio (ej. cocinafacil.com.mx) o por longitud de snippet, y escriba en RecetasCurated con valores por defecto para que luego se revisen.
3. **Promocion por uso**: otro Lambda o job que, segun RecetarioUsage, copie las recetas mas usadas desde cache a RecetasCurated (con datos ya normalizados si los tienes en cache).

---

## Resumen

- **Sí**: tiene sentido almacenar en **DynamoDB** en Alexa (cache + tablas curadas) y usar eso como base para "data warehouse" ligero.
- **Datos crudos** del MCP se pueden guardar en cache (con TTL) para no perder nada y poder curar despues.
- **Datos curados** (RecetasCurated, IngredientesCurated, PreciosCurated) son los que Alexa deberia priorizar para respuestas estables y breves.
- **RecetarioUsage** (y opcionalmente RecetarioFeedback) permite "procesar las mejores respuestas" (ordenar por uso, promover a curado, informes).
- Curación puede ser manual al principio y luego semiautomatica o por uso.

Si quieres, el siguiente paso puede ser: (1) definicion exacta de atributos de `RecetasCurated` e `IngredientesCurated` en JSON, o (2) un ejemplo de codigo Lambda (Node.js) que lea RecetasCurated y, si no hay, llame a backend-alexa y escriba en cache.
