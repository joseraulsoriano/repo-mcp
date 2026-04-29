'use client';

import { useState } from 'react';
import ShoppingOptimizer from './ShoppingOptimizer';
import { SparklesIcon, CurrencyDollarIcon, MapPinIcon } from '@heroicons/react/24/outline';
import { useShoppingList } from '@/context/ShoppingListContext';

interface MCPShoppingOptimizerProps {
  userId: string;
  presupuesto: number;
  gustos: string[];
  disgustos: string[];
  objetivo: string;
}

interface OptimizationResult {
  recipe: {
    id?: string;
    name: string;
    description?: string;
    ingredients?: { name: string }[];
  };
  bestStore: { id: string; name: string; chain: string };
  totalPrice: number;
  savings: number;
  distance: number;
  score: number;
}

export default function MCPShoppingOptimizer({
  userId,
  presupuesto,
  gustos,
  disgustos,
  objetivo
}: MCPShoppingOptimizerProps) {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<OptimizationResult[]>([]);
  const [selectedRecipe, setSelectedRecipe] = useState<OptimizationResult['recipe'] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { addToShoppingList } = useShoppingList();

  const runOptimization = async () => {
    setLoading(true);
    setError(null);
    try {
      const mcpResponse = await fetch('/api/mcp/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId,
          presupuesto,
          comidas: ['desayuno', 'comida', 'cena'],
          gustos,
          disgustos,
          objetivo,
          maxRecetasPorComida: 3,
          incluirRecetasGuardadas: true,
          actualizarPrecios: true
        })
      });
      const text = await mcpResponse.text();
      if (!mcpResponse.ok) {
        throw new Error(text);
      }
      let mcpData;
      try {
        mcpData = JSON.parse(text);
      } catch {
        throw new Error('Respuesta inválida del servidor: ' + text);
      }
      const allRecipes = Object.values(mcpData.menu).flat() as OptimizationResult['recipe'][];
      const storesResponse = await fetch('/api/stores');
      const storesText = await storesResponse.text();
      if (!storesResponse.ok) {
        throw new Error(storesText);
      }
      let storesData;
      try {
        storesData = JSON.parse(storesText);
      } catch {
        throw new Error('Respuesta inválida de tiendas: ' + storesText);
      }
      const stores = storesData.stores;
      const optimizationResults: OptimizationResult[] = [];
      for (const recipe of allRecipes) {
        try {
          const recipeOptimization = await optimizeRecipe(recipe, stores);
          if (recipeOptimization) {
            optimizationResults.push(recipeOptimization);
          }
        } catch (error) {
          console.error(`Error optimizando receta ${recipe.name}:`, error);
        }
      }
      optimizationResults.sort((a, b) => b.score - a.score);
      setResults(optimizationResults);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  const optimizeRecipe = async (recipe: OptimizationResult['recipe'], stores: { id: string; name: string; chain: string }[]): Promise<OptimizationResult | null> => {
    try {
      // Obtener precios para cada tienda
      const storePrices = [];
      
      for (const store of stores) {
        const priceResponse = await fetch('/api/stores/prices', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ingredients: recipe.ingredients,
            storeChain: store.chain
          })
        });

        if (priceResponse.ok) {
          const priceData = await priceResponse.json();
          
          // Calcular distancia (simulada por ahora)
          const distance = Math.random() * 10; // Simulado
          
          // Calcular score basado en múltiples factores
          const priceScore = 100 - (priceData.totalPrice / presupuesto) * 100;
          const distanceScore = 100 - distance * 10;
          const ingCount = recipe.ingredients?.length ?? 0;
          const availabilityScore =
            ingCount > 0 ? (priceData.availableCount / ingCount) * 100 : 0;
          
          // Ajustar score basado en preferencias
          let preferenceScore = 50; // Score base
          if (gustos.some(gusto => recipe.name.toLowerCase().includes(gusto.toLowerCase()))) {
            preferenceScore += 20;
          }
          if (disgustos.some(disgusto => recipe.name.toLowerCase().includes(disgusto.toLowerCase()))) {
            preferenceScore -= 20;
          }

          const totalScore = (priceScore * 0.4) + (distanceScore * 0.2) + (availabilityScore * 0.2) + (preferenceScore * 0.2);

          storePrices.push({
            store,
            totalPrice: priceData.totalPrice,
            distance,
            score: totalScore,
            availableCount: priceData.availableCount
          });
        }
      }

      if (storePrices.length === 0) return null;

      // Encontrar la mejor tienda
      const bestStoreData = storePrices.reduce((best, current) => 
        current.score > best.score ? current : best
      );

      // Calcular ahorro comparado con el precio más alto
      const maxPrice = Math.max(...storePrices.map(sp => sp.totalPrice));
      const savings = maxPrice - bestStoreData.totalPrice;

      return {
        recipe,
        bestStore: bestStoreData.store,
        totalPrice: bestStoreData.totalPrice,
        savings,
        distance: bestStoreData.distance,
        score: bestStoreData.score
      };
    } catch (error) {
      console.error('Error en optimizeRecipe:', error);
      return null;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Excelente';
    if (score >= 60) return 'Bueno';
    return 'Regular';
  };

  if (selectedRecipe) {
    const selectedResult = results.find((r) => {
      if (r.recipe.id != null && selectedRecipe.id != null) {
        return r.recipe.id === selectedRecipe.id;
      }
      return r.recipe.name === selectedRecipe.name;
    });
    const rowStore = selectedResult?.bestStore;
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">
            Optimización MCP: {selectedRecipe.name}
          </h2>
          <button
            onClick={() => setSelectedRecipe(null)}
            className="text-orange-600 hover:text-orange-700"
          >
            ← Volver a resultados
          </button>
        </div>
        <div className="mb-4 flex justify-end">
          <button
            className="bg-orange-600 text-white px-4 py-2 rounded-md hover:bg-orange-700 transition-colors"
            onClick={() => {
              if (selectedResult && rowStore) {
                addToShoppingList({
                  recipe: {
                    id: selectedRecipe.id ?? selectedRecipe.name,
                    name: selectedRecipe.name,
                    ingredients: selectedRecipe.ingredients,
                  },
                  store: rowStore,
                  totalPrice: selectedResult.totalPrice,
                  savings: selectedResult.savings,
                });
              }
            }}
          >
            Agregar a compras
          </button>
        </div>
        <ShoppingOptimizer
          recipe={{
            id: selectedRecipe.id ?? selectedRecipe.name,
            name: selectedRecipe.name,
            description: '',
            ingredients: (selectedRecipe.ingredients ?? []).map((ing, i) => ({
              id: `ing-${i}`,
              name: ing.name,
              quantity: 1,
              unit: 'pz',
            })),
          }}
        />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center mb-6">
        <SparklesIcon className="h-8 w-8 text-orange-600 mr-3" />
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Optimizador MCP Inteligente</h2>
          <p className="text-gray-600">Encuentra las mejores recetas y tiendas usando IA</p>
        </div>
      </div>

      <div className="mb-6">
        <button
          onClick={runOptimization}
          disabled={loading}
          className={`w-full py-3 px-4 rounded-md font-medium text-white ${
            loading
              ? 'bg-orange-400 cursor-not-allowed'
              : 'bg-orange-600 hover:bg-orange-700'
          }`}
        >
          {loading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              Optimizando con IA...
            </div>
          ) : (
            '🚀 Ejecutar Optimización MCP'
          )}
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">
            Resultados de Optimización ({results.length} recetas)
          </h3>
          
          {results.map((result, index) => (
            <div
              key={index}
              className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => setSelectedRecipe(result.recipe)}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h4 className="text-lg font-semibold text-gray-900">
                      #{index + 1} {result.recipe.name}
                    </h4>
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getScoreColor(result.score)}`}>
                      {getScoreLabel(result.score)} ({result.score.toFixed(0)})
                    </span>
                  </div>
                  
                  {(result.recipe.description?.trim().length ?? 0) > 0 ? (
                    <p className="text-gray-600 mb-2">{result.recipe.description}</p>
                  ) : null}
                  
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <div className="flex items-center">
                      <CurrencyDollarIcon className="h-4 w-4 mr-1" />
                      ${result.totalPrice.toFixed(2)}
                    </div>
                    <div className="flex items-center">
                      <MapPinIcon className="h-4 w-4 mr-1" />
                      {result.bestStore.name} ({result.distance.toFixed(1)} km)
                    </div>
                    {result.savings > 0 && (
                      <div className="text-green-600">
                        Ahorras ${result.savings.toFixed(2)}
                      </div>
                    )}
                  </div>
                </div>
                
                <button
                  className="ml-4 bg-orange-600 text-white px-4 py-2 rounded-md hover:bg-orange-700 transition-colors"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedRecipe(result.recipe);
                  }}
                >
                  Ver Detalles
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
} 