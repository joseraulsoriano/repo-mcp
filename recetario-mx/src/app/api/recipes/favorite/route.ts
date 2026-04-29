import { NextResponse } from 'next/server';

export async function POST() {
  // Simulación: podrías tener un modelo FavoriteRecipe, aquí solo lo marcamos con un campo extra si lo tuvieras
  // Por ahora, solo responde ok
  return NextResponse.json({ ok: true });
} 