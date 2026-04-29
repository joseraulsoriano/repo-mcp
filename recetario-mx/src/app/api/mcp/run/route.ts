import { NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';
import { withAccelerate } from '@prisma/extension-accelerate';
import { generarRecetasMCP } from '@/utils/mcp';
import { priceAgent } from '@/services/price-agents';

const prisma = new PrismaClient().$extends(withAccelerate());

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const {
      userId = 'dev_user_1',
      presupuesto,
      comidas = ['desayuno', 'comida', 'cena'],
      gustos = [],
      disgustos = [],
      objetivo = 'ahorrar',
      // Nuevos parámetros
      maxRecetasPorComida = 5,
      incluirRecetasGuardadas = true,
      actualizarPrecios = false,
      tiendasPreferidas = [],
    } = body;

    const preciosActualizacion: {
      solicitado: boolean;
      ejecutado: boolean;
      ingredientesActualizados?: number;
      mensaje?: string;
    } = { solicitado: Boolean(actualizarPrecios), ejecutado: false };

    if (actualizarPrecios) {
      if (priceAgent.isUpdating()) {
        preciosActualizacion.mensaje = 'Ya hay una actualización de precios en progreso';
      } else {
        const ultima = priceAgent.getLastUpdate();
        const unaHora = 60 * 60 * 1000;
        if (ultima && Date.now() - ultima.getTime() < unaHora) {
          preciosActualizacion.mensaje = 'Debes esperar al menos una hora entre actualizaciones';
        } else {
          const storePref =
            Array.isArray(tiendasPreferidas) && tiendasPreferidas.length > 0
              ? String(tiendasPreferidas[0])
              : undefined;
          try {
            const r = await priceAgent.updatePrices(userId, storePref);
            preciosActualizacion.ejecutado = true;
            preciosActualizacion.ingredientesActualizados = r.results.length;
            if (r.errors.length) {
              preciosActualizacion.mensaje = r.errors.slice(0, 3).join('; ');
            }
          } catch (e) {
            console.error('actualizarPrecios en /api/mcp/run:', e);
            preciosActualizacion.mensaje =
              e instanceof Error ? e.message : 'Error al actualizar precios';
          }
        }
      }
    }

    // Ingredientes tras el posible refresh de precios (misma lógica que POST /api/mcp/prices)
    const ingredientes = await prisma.ingredient.findMany({
      where: { userId },
      include: { recipeIngredients: true }
    });

    // Calcular presupuesto por comida
    const presupuestoDiario = Number(presupuesto) / (comidas.length || 3);

    // Generar sugerencias para cada comida
    const menu: Record<string, unknown[]> = {};
    for (const comida of comidas) {
      // Generar recetas con MCP
      const sugerenciasMCP = generarRecetasMCP({
        ingredientes,
        presupuestoDiario,
        gustos,
        disgustos,
        objetivo
      });

      // Si se incluyen recetas guardadas, obtenerlas también
      let recetasGuardadas: unknown[] = [];
      if (incluirRecetasGuardadas) {
        recetasGuardadas = await prisma.recipe.findMany({
          where: { 
            userId,
            // Filtrar por ingredientes disponibles
            ingredients: {
              some: {
                ingredient: {
                  id: { in: ingredientes.map(i => i.id) }
                }
              }
            }
          },
          include: {
            ingredients: {
              include: { ingredient: true }
            }
          }
        });
      }

      type RecipeWithIngredients = { id: string; name: string; description: string; cost?: number; ingredients: Array<{ ingredient: { name: string; price?: number; nutritionalInfo?: unknown }; unit: string; quantity: number }> };
      // Combinar y ordenar resultados
      menu[comida] = [
        ...sugerenciasMCP,
        ...(recetasGuardadas as RecipeWithIngredients[]).map((r: RecipeWithIngredients) => ({
          id: r.id,
          name: r.name,
          description: r.description,
          ingredients: r.ingredients.map((ri: { ingredient: { name: string; price?: number; nutritionalInfo?: unknown }; unit: string; quantity: number }) => ({
            name: ri.ingredient.name,
            unit: ri.unit,
            quantity: ri.quantity,
            price: ri.ingredient.price,
            nutritionalInfo: ri.ingredient.nutritionalInfo
          })),
          cost: r.cost,
          isSaved: true
        }))
      ].slice(0, maxRecetasPorComida);
    }

    // Calcular estadísticas
    type MenuItem = { cost?: number; ingredients?: { name: string }[] };
    const flatMenu = Object.values(menu).flat() as MenuItem[];
    const stats = {
      totalRecetas: flatMenu.length,
      promedioCosto: flatMenu.length ? flatMenu.reduce((sum, r) => sum + (r.cost || 0), 0) / flatMenu.length : 0,
      ingredientesUsados: [...new Set(flatMenu.flatMap(r => (r.ingredients || []).map(i => i.name)))].length
    };

    return NextResponse.json({ 
      menu,
      stats,
      metadata: {
        presupuestoDiario,
        comidas,
        objetivo,
        tiendasPreferidas,
        preciosActualizacion
      }
    });

  } catch (error) {
    console.error('Error en MCP:', error);
    return NextResponse.json(
      { error: 'Error al generar el menú' },
      { status: 500 }
    );
  }
} 