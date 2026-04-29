'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import Navigation from '@/components/Navigation';

export function ConditionalLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isAuth = pathname?.startsWith('/auth') ?? false;

  if (isAuth) {
    return <>{children}</>;
  }

  return (
    <>
      <Navigation />
      <main className="min-h-screen bg-gray-50">{children}</main>
      <footer className="border-t border-gray-200 bg-white py-4 text-center text-sm text-gray-500">
        <Link href="/privacy" className="hover:text-orange-600">
          Politica de privacidad (Skill Alexa)
        </Link>
      </footer>
    </>
  );
}
