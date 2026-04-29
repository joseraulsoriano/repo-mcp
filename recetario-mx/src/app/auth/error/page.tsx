'use client';

import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';

const MESSAGES: Record<string, string> = {
  Configuration: 'Hay un problema de configuración del servidor. Intenta más tarde.',
  AccessDenied: 'No tienes permiso para acceder.',
  Verification: 'El enlace de verificación expiró o ya se usó.',
  Default: 'Ocurrió un error al iniciar sesión.',
};

function AuthErrorContent() {
  const searchParams = useSearchParams();
  const code = searchParams.get('error') || undefined;
  const text = (code && MESSAGES[code]) || MESSAGES.Default;

  return (
    <div className="relative min-h-screen overflow-hidden bg-stone-950 px-4 py-16">
      <div
        className="pointer-events-none absolute inset-0 bg-gradient-to-b from-stone-900/80 via-stone-900 to-stone-100"
        aria-hidden
      />
      <div className="relative mx-auto max-w-md rounded-2xl border border-white/10 bg-white/95 p-8 text-center shadow-xl backdrop-blur-md sm:p-10">
        <h1 className="text-xl font-semibold text-stone-900">No se pudo completar el acceso</h1>
        <p className="mt-3 text-sm leading-relaxed text-stone-600">{text}</p>
        <Link
          href="/auth/signin"
          className="mt-6 inline-flex rounded-xl bg-orange-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-orange-600/25 transition hover:bg-orange-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-orange-600"
        >
          Volver al inicio de sesión
        </Link>
      </div>
    </div>
  );
}

function Fallback() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-stone-950">
      <div className="h-10 w-10 animate-spin rounded-full border-2 border-orange-500 border-t-transparent" />
    </div>
  );
}

export default function AuthErrorPage() {
  return (
    <Suspense fallback={<Fallback />}>
      <AuthErrorContent />
    </Suspense>
  );
}
