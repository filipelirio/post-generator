"use client";

import { useEffect, useState } from "react";
import { BarChart, FileText, CheckCircle, Clock3, List, Sparkles } from "lucide-react";
import Link from "next/link";
import { toast } from "react-hot-toast";

import api from "@/lib/api";

type EditorialPauta = {
  ID: string;
  Status: string;
};

export default function DashboardPage() {
  const [pautas, setPautas] = useState<EditorialPauta[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const fetchPautas = async () => {
    setLoading(true);
    try {
      const response = await api.get("/editorial/pautas");
      setPautas(response.data);
    } catch (error) {
      console.error("Erro ao buscar métricas editoriais:", error);
      toast.error("Erro ao carregar o dashboard editorial.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPautas();
  }, []);

  const handleGeneratePautas = async () => {
    setGenerating(true);
    const toastId = toast.loading("Gerando 10 novas pautas com web search...");
    try {
      const response = await api.post("/editorial/pautas/generate", { count: 10 });
      toast.success(`${response.data.created_count} pautas criadas com sucesso.`, { id: toastId });
      fetchPautas();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Erro ao gerar pautas.", { id: toastId });
    } finally {
      setGenerating(false);
    }
  };

  const metrics = {
    total: pautas.length,
    pendentes: pautas.filter((p) => p.Status === "Pendente").length,
    geradas: pautas.filter((p) => ["Em producao", "Rascunho", "Publicado"].includes(p.Status)).length,
    publicadas: pautas.filter((p) => p.Status === "Publicado").length,
  };

  const cards = [
    { title: "Total de Pautas", value: metrics.total, icon: FileText, color: "bg-blue-50 text-blue-600" },
    { title: "Pautas Pendentes", value: metrics.pendentes, icon: Clock3, color: "bg-amber-50 text-amber-600" },
    { title: "Artigos Gerados", value: metrics.geradas, icon: BarChart, color: "bg-orange-50 text-orange-600" },
    { title: "Publicados WP", value: metrics.publicadas, icon: CheckCircle, color: "bg-green-50 text-green-600" },
  ];

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Operação Editorial Easy Medicina</h2>
          <p className="text-sm text-slate-500">Pautas em Excel local, geração com GPT + web search, capa automática e publicação no WordPress.</p>
        </div>
        <button
          onClick={handleGeneratePautas}
          disabled={generating}
          className="inline-flex items-center gap-2 rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <Sparkles className={`h-4 w-4 ${generating ? "animate-pulse" : ""}`} />
          <span>Gerar 10 Novas Pautas</span>
        </button>
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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900 mb-2">Fila Editorial</h3>
          <p className="text-sm text-slate-600 mb-4">Acompanhe a planilha local, gere artigos com SEO completo e envie ao WordPress com Yoast e imagem destacada.</p>
          <Link href="/pautas" className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">
            <List className="h-4 w-4" />
            <span>Ver Pautas</span>
          </Link>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900 mb-2">Geração Automatizada</h3>
          <p className="text-sm text-slate-600 mb-4">O GPT usa web search para pauta, links internos, links externos, CTA e propaganda dos produtos da Easy Medicina.</p>
          <button
            onClick={handleGeneratePautas}
            disabled={generating}
            className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <Sparkles className="h-4 w-4" />
            <span>Abastecer a fila agora</span>
          </button>
        </div>
      </div>
    </div>
  );
}
