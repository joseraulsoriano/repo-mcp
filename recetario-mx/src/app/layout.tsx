import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ConditionalLayout } from "@/components/ConditionalLayout";
import { ShoppingListProvider } from "@/context/ShoppingListContext";
import { Providers } from "./providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Recetario MX - Tu asistente personal de cocina",
  description: "Gestiona tus recetas, presupuesto y tiempo de cocina de manera eficiente",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className={inter.className}>
        <Providers>
          <ShoppingListProvider>
            <ConditionalLayout>{children}</ConditionalLayout>
          </ShoppingListProvider>
        </Providers>
      </body>
    </html>
  );
}
