# Recetario MX 🍳

Recetario MX es una aplicación web moderna para compartir y descubrir recetas tradicionales mexicanas. Desarrollada con tecnologías modernas, esta plataforma permite a los usuarios explorar, compartir y guardar sus recetas favoritas de la gastronomía mexicana.

## Características Principales 🌟

- 📱 Interfaz moderna y responsive
- 🔍 Búsqueda y filtrado de recetas
- 📍 Integración con mapas para ubicar ingredientes y restaurantes
- 📝 Sistema de recetas paso a paso
- 🖼️ Soporte para imágenes de alta calidad
- 🔐 Autenticación de usuarios

## Tecnologías Utilizadas 🛠️

- [Next.js](https://nextjs.org/) - Framework de React para aplicaciones web
- [TypeScript](https://www.typescriptlang.org/) - Superset tipado de JavaScript
- [Prisma](https://www.prisma.io/) - ORM moderno para base de datos
- [Tailwind CSS](https://tailwindcss.com/) - Framework CSS utility-first
- [Google Maps API](https://developers.google.com/maps) - Integración de mapas

## Requisitos Previos 📋

- Node.js 18.x o superior
- npm o yarn
- Base de datos PostgreSQL

## Instalación 🚀

1. Navega al directorio del proyecto:
```bash
cd recetario-mx
```

2. Instala las dependencias:
```bash
npm install
# o
yarn install
```

3. Configura las variables de entorno:
   - Crea un archivo `.env` basado en `.env.example`
   - Añade las variables necesarias (API keys, etc.)

4. Inicia el servidor de desarrollo:
```bash
npm run dev
# o
yarn dev
```

Abre [http://localhost:3000](http://localhost:3000) en tu navegador para ver la aplicación.

## Backend Alexa y skill Alexa

- **backend-alexa/**: Backend Node.js para la skill Alexa Recetario MX. Expone `/api/mcp/recipes`, `/api/mcp/ingredients`, etc. y puede conectarse al motor MCP (recetario-mcp) para busqueda real. Ver `backend-alexa/README.md`.
- **ALEXA_SETUP.md**: Configuracion de la skill en Alexa Developer Console (nombre, locale, intents, endpoint).
- **DATA_LAYER.md**: Diseño DynamoDB y single-table para recetas curadas y cache.

La skill (Lambda) llama a este backend; el backend opcionalmente llama a **recetario-mcp** (proyecto aparte) para recetas/ingredientes/precios desde Brave Search.

## Estructura del Proyecto 📁

```
recetario-mx/
├── src/              # Código fuente principal (Next.js)
├── backend-alexa/    # Backend para skill Alexa (Node.js, /api/mcp/*)
├── prisma/           # Esquemas y migraciones de la base de datos
├── public/           # Archivos estáticos
├── scripts/          # Scripts de utilidad
├── ALEXA_SETUP.md    # Guia skill Alexa
├── DATA_LAYER.md     # DynamoDB y curación
└── ...
```
## UX
<img width="1470" alt="Captura de pantalla 2025-06-13 a la(s) 22 50 25" src="https://github.com/user-attachments/assets/86ef6746-72a6-4855-85e0-6ec80cd1de93" />

<img width="1470" alt="Captura de pantalla 2025-06-13 a la(s) 22 50 54" src="https://github.com/user-attachments/assets/dbcd8ff1-e448-44fa-8402-b7c0bd83fc99" />

<img width="1470" alt="Captura de pantalla 2025-06-13 a la(s) 22 51 31" src="https://github.com/user-attachments/assets/64964b14-633a-4786-83c7-d3fb8449b7dd" />
<img width="1470" alt="Captura de pantalla 2025-06-13 a la(s) 22 52 17" src="https://github.com/user-attachments/assets/4ceca9d3-f81d-4c51-ab8b-7cd4d94af4d0" />
<img width="1470" alt="Captura de pantalla 2025-06-13 a la(s) 22 52 31" src="https://github.com/user-attachments/assets/d490ba37-34b7-402f-b5e3-742800b7fdd0" />
<img width="1470" alt="Captura de pantalla 2025-06-13 a la(s) 22 53 27" src="https://github.com/user-attachments/assets/da75875d-75ef-4c8a-84a4-2fe3f8d58309" />
<img width="1470" alt="Captura de pantalla 2025-06-13 a la(s) 22 54 07" src="https://github.com/user-attachments/assets/0918b19c-01a1-4399-ab9e-df156480a84c" />
<img width="1470" alt="Captura de pantalla 2025-06-13 a la(s) 22 54 50" src="https://github.com/user-attachments/assets/379acaa3-96ca-48e3-b37d-5b4bd3c856ef" />

<img width="1470" alt="Captura de pantalla 2025-06-13 a la(s) 22 56 25" src="https://github.com/user-attachments/assets/14d904ff-2336-4e93-8ede-d05fd69db6b6" />
<img width="1470" alt="Captura de pantalla 2025-06-13 a la(s) 22 56 40" src="https://github.com/user-attachments/assets/7635e12c-d390-4103-ac50-f501d3dedd45" />

<img width="1470" alt="Captura de pantalla 2025-06-13 a la(s) 22 56 51" src="https://github.com/user-attachments/assets/96e8d3a9-9621-4db7-8332-054795171c47" />


## Estructura del Proyecto Detallada 📁

```
recetario-mx/
├── src/
│   ├── app/              # Rutas y páginas de Next.js
│   │   ├── api/          # Endpoints API
│   │   │   ├── mcp/      # Endpoints MCP
│   │   │   ├── auth/     # Autenticación
│   │   │   ├── recipes/  # Recetas
│   │   │   ├── ingredients/ # Ingredientes
│   │   │   └── stores/   # Tiendas
│   │   ├── ingredients/  # Páginas de ingredientes
│   │   ├── recipes/      # Páginas de recetas
│   │   └── ...
│   ├── components/       # Componentes React
│   ├── context/          # Context API
│   ├── services/         # Servicios y agentes
│   ├── types/            # Tipos TypeScript
│   └── utils/            # Utilidades
├── prisma/               # Esquemas y migraciones
├── scripts/              # Scripts de utilidad
└── public/               # Archivos estáticos
```

## Características Técnicas 🔧

### MCP Integration
- Endpoints MCP para ingredientes, precios, recetas y sugerencias
- Integración con Model Context Protocol
- Agentes de precios automáticos

### Base de Datos
- Prisma ORM para gestión de base de datos
- Migraciones automatizadas
- Seed scripts para datos iniciales

### Funcionalidades Principales
- Sistema de autenticación con NextAuth
- OCR para extracción de texto de tickets
- Optimizador de compras inteligente
- Seguimiento de precios de ingredientes
- Integración con Google Maps para ubicación de tiendas

## Variables de Entorno 🔐

Crea un archivo `.env` con las siguientes variables:

```
DATABASE_URL="postgresql://..."
NEXTAUTH_SECRET="..."
NEXTAUTH_URL="http://localhost:3000"
GOOGLE_MAPS_API_KEY="..."
```

## Comandos Disponibles 📝

```bash
npm run dev      # Desarrollo
npm run build    # Producción
npm run start    # Servidor producción
npm run lint     # Linter
npm run seed     # Seed de base de datos
```

## Recursos de Aprendizaje 📚

- [Next.js Documentation](https://nextjs.org/docs)
- [Prisma Documentation](https://www.prisma.io/docs)
- [NextAuth.js](https://next-auth.js.org/)
