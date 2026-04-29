'use client';

import { signIn } from 'next-auth/react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { FormEvent, useState } from 'react';

export function SignInForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const callbackUrl = searchParams.get('callbackUrl') || '/dashboard';
  const justRegistered = searchParams.get('registered') === '1';

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const result = await signIn('credentials', {
        email: email.trim(),
        password,
        redirect: false,
        callbackUrl,
      });
      if (result?.error) {
        setError('Usuario o contraseña incorrectos. Revisa tus datos e inténtalo de nuevo.');
        return;
      }
      router.push(callbackUrl);
      router.refresh();
    } catch {
      setError('No se pudo conectar. Comprueba tu red e inténtalo más tarde.');
    } finally {
      setLoading(false);
    }
  }

  const disabled = loading || !email.trim() || !password;

  return (
    <div className="relative min-h-screen overflow-hidden bg-stone-950 px-4 py-10 sm:py-16">
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(234,88,12,0.35),transparent)]"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute inset-0 bg-gradient-to-b from-stone-900/80 via-stone-900 to-stone-100"
        aria-hidden
      />

      <div className="relative mx-auto flex min-h-[calc(100vh-5rem)] max-w-md flex-col justify-center sm:min-h-[calc(100vh-8rem)]">
        <div className="mb-6 text-center sm:mb-8">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-white/90 transition hover:text-white"
          >
            <span className="text-2xl" aria-hidden>
              🍳
            </span>
            <span className="text-lg font-semibold tracking-tight">Recetario MX</span>
          </Link>
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/95 p-8 shadow-[0_25px_50px_-12px_rgba(0,0,0,0.35)] backdrop-blur-md sm:p-10">
          <header className="mb-8 text-center">
            <h1 className="text-2xl font-semibold tracking-tight text-stone-900">Iniciar sesión</h1>
            <p className="mt-2 text-sm leading-relaxed text-stone-600">
              Accede a tu cocina digital: recetas, presupuesto e ingredientes en un solo lugar.
            </p>
          </header>

          {justRegistered ? (
            <p
              role="status"
              className="mb-5 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
            >
              Cuenta creada. Inicia sesión con tu correo y contraseña.
            </p>
          ) : null}

          <form onSubmit={onSubmit} className="space-y-5">
            <div>
              <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-stone-800">
                Correo
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                aria-invalid={!!error}
                className="w-full rounded-xl border border-stone-200 bg-white px-4 py-3 text-stone-900 shadow-inner shadow-stone-900/5 outline-none transition placeholder:text-stone-400 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/25"
                placeholder="tu@correo.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-stone-800">
                Contraseña
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                aria-invalid={!!error}
                aria-describedby={error ? 'signin-error' : undefined}
                className="w-full rounded-xl border border-stone-200 bg-white px-4 py-3 text-stone-900 shadow-inner shadow-stone-900/5 outline-none transition placeholder:text-stone-400 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/25"
                placeholder="Tu contraseña"
              />
            </div>

            {error ? (
              <p
                id="signin-error"
                role="alert"
                className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
              >
                {error}
              </p>
            ) : null}

            <button
              type="submit"
              disabled={disabled}
              className="flex w-full items-center justify-center rounded-xl bg-orange-600 px-4 py-3.5 text-sm font-semibold text-white shadow-lg shadow-orange-600/30 transition hover:bg-orange-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-orange-600 disabled:pointer-events-none disabled:opacity-50 active:scale-[0.99]"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span
                    className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"
                    aria-hidden
                  />
                  Entrando…
                </span>
              ) : (
                'Entrar'
              )}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-stone-600">
            ¿Sin cuenta?{' '}
            <Link href="/auth/signup" className="font-medium text-orange-600 underline-offset-4 hover:underline">
              Crear cuenta
            </Link>
          </p>
        </div>

        <p className="mt-8 text-center text-sm text-stone-700 sm:text-stone-600">
          <Link href="/" className="font-medium text-orange-700 underline-offset-4 hover:underline">
            Volver al inicio
          </Link>
        </p>
      </div>
    </div>
  );
}
