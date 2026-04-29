import { NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export async function PUT(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    const data = await request.json();
    const ingredient = await prisma.ingredient.update({
      where: { id },
      data,
    });
    return NextResponse.json(ingredient);
  } catch {
    return NextResponse.json({ error: 'Error al actualizar ingrediente' }, { status: 500 });
  }
}

export async function DELETE(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id } = await params;
    await prisma.ingredient.delete({ where: { id } });
    return NextResponse.json({ ok: true });
  } catch {
    return NextResponse.json({ error: 'Error al eliminar ingrediente' }, { status: 500 });
  }
} 