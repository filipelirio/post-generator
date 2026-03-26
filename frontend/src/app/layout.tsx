import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "@/styles/globals.css";
import Sidebar from "@/components/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Gerador de Artigos AI | Easy Medicina",
  description: "Geração de artigos otimizados para SEO com Gemini para WordPress.",
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
          <div className="ml-64 flex-1 flex flex-col overflow-hidden">
            {/* Topbar / Navbar simples */}
            <header className="flex h-16 items-center border-b border-slate-200 bg-white px-8">
              <h1 className="text-lg font-semibold text-slate-800">Painel de Controle</h1>
            </header>

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto p-8">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
