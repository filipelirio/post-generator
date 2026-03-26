"use client";

import { useEffect, useState } from "react";
import { BarChart, FileText, CheckCircle, AlertCircle, UploadCloud, List } from "lucide-react";
import Link from "next/link";
import api from "@/lib/api";

export default function DashboardPage() {
  const [metrics, setMetrics] = useState({
    total: 0,
    geradas: 0,
    publicadas: 0,
    erro: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchMetrics() {
      try {
        const response = await api.get("/pautas/");
        const pautas = response.data;

        const stats = {
          total: pautas.length,
          geradas: pautas.filter((p: any) => p.status === "gerada").length,
          publicadas: pautas.filter((p: any) => p.status === "publicada").length,
          erro: pautas.filter((p: any) => p.status === "erro").length,
        };
        setMetrics(stats);
      } catch (error) {
        console.error("Erro ao buscar métricas:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchMetrics();
  }, []);

  const cards = [
    { title: "Total de Pautas", value: metrics.total, icon: FileText, color: "bg-blue-50 text-blue-600" },
    { title: "Artigos Gerados", value: metrics.geradas, icon: BarChart, color: "bg-orange-50 text-orange-600" },
    { title: "Publicados WP", value: metrics.publicadas, icon: CheckCircle, color: "bg-green-50 text-green-600" },
    { title: "Com Erro", value: metrics.erro, icon: AlertCircle, color: "bg-red-50 text-red-600" },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Bem-vindo ao Easy Artigos</h2>
        <p className="text-sm text-slate-500">Crie, gerencie e publique artigos otimizados com IA.</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 animate-pulse">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-32 rounded-xl bg-slate-100" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {cards.map((card) => {
            const Icon = card.icon;
            return (
              <div key={card.title} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex items-center gap-4">
                  <div className={`rounded-lg p-3 ${card.color}`}>
                    <Icon className="h-6 w-6" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-500">{card.title}</p>
                    <p className="text-2xl font-bold text-slate-900">{card.value}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Ações Rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900 mb-2">Primeiros Passos</h3>
          <p className="text-sm text-slate-600 mb-4">Importe uma planilha Excel (.xlsx) com suas pautas para começar a gerar conteúdo.</p>
          <Link href="/import" className="inline-flex items-center gap-2 rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700">
            <UploadCloud className="h-4 w-4" />
            <span>Importar Planilha</span>
          </Link>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900 mb-2">Lista de Pautas</h3>
          <p className="text-sm text-slate-600 mb-4">Visualize todas as pautas importadas, seus status e clique para gerar os artigos.</p>
          <Link href="/pautas" className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">
            <List className="h-4 w-4" />
            <span>Ver Pautas</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
