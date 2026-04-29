# 🚀 Pasos Inmediatos para Mejorar Proyectos MCP

## ⚡ Quick Wins (Hacer HOY - 2-3 horas)

### 1. Crear .env.example para volunteer-mcp (15 minutos)

**Crear `volunteer-mcp/.env.example`:**

```env
# Brave Search API (Opcional - mejora búsquedas)
BRAVE_API_KEY=your_brave_api_key_here
BRAVE_MAX_RPS=0.8
BRAVE_MONTHLY_QUOTA=2000

# Redis (Opcional - para caché y persistencia)
REDIS_URL=redis://localhost:6379

# Database (Opcional - usa SQLite por defecto si no se especifica)
DATABASE_URL=postgresql://user:password@localhost:5432/volunteer_db

# Logging
LOG_LEVEL=INFO
```

**Actualizar README.md:**
- Agregar sección sobre variables de entorno
- Referencia al .env.example

---

### 2. Crear .env.example para recetario-mx (15 minutos)

**Crear `recetario-mx/.env.example`:**

```env
# Database
DATABASE_URL="file:./dev.db"

# NextAuth
NEXTAUTH_SECRET=your_nextauth_secret_here_generate_with_openssl_rand_base64_32
NEXTAUTH_URL=http://localhost:3000

# Google Maps API (Opcional)
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# Node Environment
NODE_ENV=development
```

**Instrucciones en README:**
```markdown
## Configuración

1. Copia el archivo `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```

2. Completa las variables necesarias:
   - `NEXTAUTH_SECRET`: Genera uno con `openssl rand -base64 32`
   - `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY`: Obtén una en Google Cloud Console

3. Inicia la base de datos:
   ```bash
   npx prisma migrate dev
   ```
```

---

### 3. Implementar TODO Pendiente (1 hora)

**Archivo:** `recetario-mx/src/app/api/mcp/run/route.ts`

**Reemplazar líneas 32-36:**

```typescript
// ANTES:
if (actualizarPrecios) {
  // TODO: Implementar actualización de precios con el scraper
  // Por ahora solo un placeholder
  console.log('Actualizando precios...');
}

// DESPUÉS:
if (actualizarPrecios) {
  try {
    const { updatePrices } = await import('@/services/price-agents');
    const result = await updatePrices(userId, tiendasPreferidas[0]);
    
    if (result.errors && result.errors.length > 0) {
      console.warn('Algunos precios no se pudieron actualizar:', result.errors);
    }
    
    console.log(`Precios actualizados: ${result.results.length} ingredientes`);
  } catch (error) {
    console.error('Error al actualizar precios:', error);
    // No fallar el proceso completo si la actualización falla
  }
}
```

**Alternativa si no se implementará:**
```typescript
if (actualizarPrecios) {
  return NextResponse.json(
    { error: 'La actualización de precios no está disponible actualmente' },
    { status: 501 }
  );
}
```

---

### 4. Agregar Error Boundary Básico (30 minutos)

**Crear `recetario-mx/src/components/ErrorBoundary.tsx`:**

```typescript
'use client';

import React from 'react';

interface Props {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error: Error; reset: () => void }>;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error capturado por ErrorBoundary:', error, errorInfo);
    // Aquí puedes enviar a un servicio de logging
  }

  render() {
    if (this.state.hasError) {
      const Fallback = this.props.fallback || DefaultErrorFallback;
      return (
        <Fallback
          error={this.state.error!}
          reset={() => this.setState({ hasError: false, error: null })}
        />
      );
    }

    return this.props.children;
  }
}

function DefaultErrorFallback({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
        <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full mb-4">
          <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h2 className="text-xl font-bold text-gray-900 mb-2 text-center">Algo salió mal</h2>
        <p className="text-gray-600 mb-4 text-center text-sm">{error.message}</p>
        <button
          onClick={reset}
          className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Intentar de nuevo
        </button>
      </div>
    </div>
  );
}
```

**Usar en `recetario-mx/src/app/layout.tsx`:**

```typescript
import { ErrorBoundary } from '@/components/ErrorBoundary';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
      </body>
    </html>
  );
}
```

---

## 🔧 Mejoras Semana 1

### 5. Agregar Toast Notifications (2 horas)

**Instalar librería:**
```bash
cd recetario-mx
npm install react-hot-toast
```

**Crear `recetario-mx/src/components/Toaster.tsx`:**
```typescript
'use client';

import { Toaster as HotToaster } from 'react-hot-toast';

export function Toaster() {
  return (
    <HotToaster
      position="top-right"
      toastOptions={{
        duration: 4000,
        style: {
          background: '#363636',
          color: '#fff',
        },
        success: {
          duration: 3000,
          iconTheme: {
            primary: '#4ade80',
            secondary: '#fff',
          },
        },
        error: {
          duration: 5000,
          iconTheme: {
            primary: '#ef4444',
            secondary: '#fff',
          },
        },
      }}
    />
  );
}
```

**Usar en componentes:**
```typescript
import toast from 'react-hot-toast';

// Éxito
toast.success('Receta guardada correctamente');

// Error
toast.error('Error al guardar la receta');

// Cargando
const toastId = toast.loading('Guardando...');
// ... operación
toast.success('Guardado!', { id: toastId });
```

---

### 6. Validación Robusta en APIs (3 horas)

**Crear `recetario-mx/src/lib/validations.ts`:**
```typescript
import { z } from 'zod';

export const recipeSchema = z.object({
  name: z.string().min(1, 'El nombre es requerido').max(100),
  description: z.string().min(10).max(500),
  instructions: z.string().min(20),
  prepTime: z.number().int().positive(),
  cookTime: z.number().int().positive(),
  servings: z.number().int().positive(),
  difficulty: z.enum(['fácil', 'medio', 'difícil']),
  cost: z.number().nonnegative(),
});

export const ingredientSchema = z.object({
  name: z.string().min(1),
  quantity: z.number().positive(),
  unit: z.string().min(1),
  price: z.number().nonnegative().optional(),
  category: z.enum(['CEREALES', 'TUBERCULOS', 'LEGUMINOSAS', 'PROTEINAS', 'VERDURAS']),
});
```

**Usar en API routes:**
```typescript
import { recipeSchema } from '@/lib/validations';
import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const validated = recipeSchema.parse(body);
    // ... procesar
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validación fallida', details: error.errors },
        { status: 400 }
      );
    }
    throw error;
  }
}
```

---

### 7. Clarificar MCP o Renombrar (1 hora)

**Opción A: Renombrar para clarificar**

**Renombrar función:**
```typescript
// De:
export function generarRecetasMCP(...)

// A:
export function generarRecetasLocales(...)
// o
export function sugerirRecetasBasadasEnIngredientes(...)
```

**Actualizar README:**
```markdown
## Generación de Recetas

El sistema usa un algoritmo local para sugerir recetas basadas en:
- Ingredientes disponibles
- Presupuesto
- Preferencias del usuario
- Objetivos nutricionales

**Nota:** Actualmente no usa un servidor MCP externo para generación de recetas.
```

**Opción B: Conectar con MCP Real**

Si quieres conectar con un servidor MCP real, necesitarías:

```typescript
async function generarRecetasConMCP(options: MCPOptions) {
  const response = await fetch('http://tu-servidor-mcp/api/generate-recipes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(options),
  });
  return response.json();
}
```

---

## 🗄️ Mejoras Próximo Mes

### 8. Agregar Tests Básicos (6-8 horas)

**Instalar dependencias:**
```bash
cd recetario-mx
npm install -D vitest @testing-library/react @testing-library/jest-dom
```

**Crear `recetario-mx/vitest.config.ts`:**
```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

**Crear tests básicos:**
```typescript
// src/utils/mcp.test.ts
import { describe, it, expect } from 'vitest';
import { generarRecetasMCP } from './mcp';

describe('generarRecetasMCP', () => {
  it('debe retornar array vacío si no hay ingredientes', () => {
    const result = generarRecetasMCP({
      ingredientes: [],
      presupuestoDiario: 100,
      gustos: [],
      disgustos: [],
      objetivo: 'ahorrar',
    });
    expect(result).toEqual([]);
  });

  // Más tests...
});
```

---

### 9. Mejorar Logging en volunteer-mcp (2 horas)

**Crear `volunteer-mcp/logger.py`:**
```python
import logging
import sys
from datetime import datetime

def setup_logger(name: str, level: str = "INFO"):
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Formato estructurado
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    return logger

# Usar en main.py
logger = setup_logger(__name__)
```

**Reemplazar `print` y `console.log` por `logger.info/error/warning`**

---

## ✅ Checklist de Implementación

### HOY (2-3 horas)
- [ ] Crear .env.example para volunteer-mcp
- [ ] Crear .env.example para recetario-mx
- [ ] Implementar TODO pendiente
- [ ] Agregar Error Boundary básico

### Esta Semana (8-10 horas)
- [ ] Toast notifications
- [ ] Validación robusta en APIs
- [ ] Clarificar o renombrar MCP
- [ ] Mejorar manejo de errores

### Próximo Mes (15-20 horas)
- [ ] Tests unitarios básicos
- [ ] Tests de integración
- [ ] Mejorar logging
- [ ] Documentación técnica expandida
- [ ] Performance optimization

---

## 🔍 Validación Post-Implementación

Después de hacer cambios, verificar:

1. **Variables de entorno:**
   ```bash
   # Verificar que .env.example existe
   ls volunteer-mcp/.env.example
   ls recetario-mx/.env.example
   ```

2. **Error Boundary:**
   - Forzar error en componente
   - Verificar que se muestra mensaje de error
   - Probar botón "Intentar de nuevo"

3. **Validación:**
   - Enviar datos inválidos a API
   - Verificar respuesta 400 con detalles

4. **TODO:**
   - Buscar TODOs en código
   ```bash
   grep -r "TODO" recetario-mx/src
   ```

---

**Última actualización:** 2024-01-XX
**Prioridad:** 🟡 Media - Optimización incremental
**Tiempo total estimado:** 25-33 horas para todas las mejoras

