import type { Metadata } from "next";
import { Inter } from "next/font/google";

import Sidebar from "@/components/Sidebar";
import "@/styles/globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Gerador de Artigos AI | Easy Medicina",
  description: "Fluxo editorial da Easy Medicina com GPT, web search, capa automatica e publicacao no WordPress.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body className={inter.className}>
        <div className="flex h-screen bg-slate-50">
          <Sidebar />
          <div className="ml-64 flex flex-1 flex-col overflow-hidden">
            <header className="flex h-16 items-center border-b border-slate-200 bg-white px-8">
              <h1 className="text-lg font-semibold text-slate-800">Painel de Controle</h1>
            </header>

            <main className="flex-1 overflow-y-auto p-8">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
