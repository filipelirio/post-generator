"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Search, Filter, Eye, Sparkles, Clock3, CheckCircle2, FileText, Loader2, RefreshCw } from "lucide-react";
import clsx from "clsx";
import { toast } from "react-hot-toast";

import api from "@/lib/api";

type EditorialPauta = {
  ID: string;
  Status: string;
  Prioridade: string;
  Tema: string;
  "Titulo sugerido": string;
  Categoria: string;
  "Palavra-chave principal": string;
  "Posicao no funil": string;
  "CTA sugerido": string;
  "Produto sugerido": string;
  "Data publicacao": string;
  "URL WordPress": string;
};

export default function PautasPage() {
  const [pautas, setPautas] = useState<EditorialPauta[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [generatingPautas, setGeneratingPautas] = useState(false);
  const [generatingArticleId, setGeneratingArticleId] = useState<string | null>(null);
  const [syncingStatuses, setSyncingStatuses] = useState(false);

  const fetchPautas = async () => {
    setLoading(true);
    try {
      const response = await api.get("/editorial/pautas");
      setPautas(response.data);
    } catch (error) {
      console.error("Erro ao buscar pautas:", error);
      toast.error("Erro ao carregar pautas editoriais.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPautas();
  }, []);

  const filteredPautas = useMemo(() => {
    return pautas.filter((pauta) => {
      const matchesSearch =
        !search ||
        pauta.Tema.toLowerCase().includes(search.toLowerCase()) ||
        pauta["Palavra-chave principal"].toLowerCase().includes(search.toLowerCase()) ||
        pauta["Titulo sugerido"].toLowerCase().includes(search.toLowerCase());
      const matchesStatus = !statusFilter || pauta.Status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [pautas, search, statusFilter]);

  const handleGeneratePautas = async () => {
    setGeneratingPautas(true);
    const toastId = toast.loading("Gerando 10 novas pautas...");
    try {
      const response = await api.post("/editorial/pautas/generate", { count: 10 });
      toast.success(`${response.data.created_count} pautas criadas.`, { id: toastId });
      fetchPautas();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Erro ao gerar pautas.", { id: toastId });
    } finally {
      setGeneratingPautas(false);
    }
  };

  const handleSyncWordPressStatuses = async () => {
    setSyncingStatuses(true);
    const toastId = toast.loading("Sincronizando status com o WordPress...");
    try {
      const response = await api.post("/editorial/pautas/sync-wordpress");
      toast.success(response.data.message || "Status sincronizados.", { id: toastId });
      await fetchPautas();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Erro ao sincronizar status.", { id: toastId });
    } finally {
      setSyncingStatuses(false);
    }
  };

  const handleGenerateArticle = async (id: string) => {
    setGeneratingArticleId(id);
    const toastId = toast.loading("Gerando artigo, SEO e capa...");
    try {
      await api.post(`/editorial/articles/${id}/generate`);
      toast.success("Artigo gerado com sucesso.", { id: toastId });
      await fetchPautas();
      window.location.href = `/pautas/${id}/review`;
    } catch (error: any) {
      console.error("Erro ao gerar artigo:", error);
      toast.error(error.response?.data?.detail || "Erro na geração do artigo.", { id: toastId });
    } finally {
      setGeneratingArticleId(null);
    }
  };

  const statusStyles: Record<string, string> = {
    Pendente: "bg-slate-100 text-slate-700 border-slate-200",
    "Em producao": "bg-amber-50 text-amber-700 border-amber-200",
    Rascunho: "bg-blue-50 text-blue-700 border-blue-200",
    Publicado: "bg-green-50 text-green-700 border-green-200",
  };

  const canReview = (status: string) => ["Em producao", "Rascunho", "Publicado"].includes(status);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Fila de Pautas</h2>
          <p className="text-sm text-slate-500">Planilha local + GPT com web search + publicação no WordPress com Yoast e imagem.</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleSyncWordPressStatuses}
            disabled={syncingStatuses || loading}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {syncingStatuses ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
            <span>Atualizar status WP</span>
          </button>
          <button
            onClick={handleGeneratePautas}
            disabled={generatingPautas}
            className="inline-flex items-center gap-2 rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {generatingPautas ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
            <span>Gerar 10 Novas Pautas</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm md:grid-cols-3">
        <div className="relative md:col-span-2">
          <label className="text-xs font-semibold text-slate-500 uppercase mb-1 block">Busca</label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Tema, título sugerido ou keyword..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50 focus:outline-none focus:ring-2 focus:ring-green-500 transition-all"
            />
          </div>
        </div>

        <div>
          <label className="text-xs font-semibold text-slate-500 uppercase mb-1 block">Status</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Todos os status</option>
            <option value="Pendente">Pendente</option>
            <option value="Em producao">Em produção</option>
            <option value="Rascunho">Rascunho</option>
            <option value="Publicado">Publicado</option>
          </select>
        </div>
      </div>

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-xs font-semibold uppercase text-slate-500">
                <th className="px-6 py-4">Tema</th>
                <th className="px-6 py-4">Keyword</th>
                <th className="px-6 py-4">Produto</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm text-slate-700">
              {loading ? (
                [1, 2, 3, 4].map((i) => (
                  <tr key={i} className="animate-pulse">
                    <td className="px-6 py-4"><div className="h-4 w-56 bg-slate-100 rounded mb-2" /><div className="h-3 w-32 bg-slate-50 rounded" /></td>
                    <td className="px-6 py-4"><div className="h-4 w-28 bg-slate-100 rounded" /></td>
                    <td className="px-6 py-4"><div className="h-4 w-24 bg-slate-100 rounded" /></td>
                    <td className="px-6 py-4"><div className="h-6 w-24 bg-slate-100 rounded-full" /></td>
                    <td className="px-6 py-4"><div className="h-8 w-28 bg-slate-100 ml-auto rounded" /></td>
                  </tr>
                ))
              ) : filteredPautas.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center">
                    <div className="flex flex-col items-center justify-center text-slate-400">
                      <Filter className="h-12 w-12 mb-4 opacity-20" />
                      <p className="text-lg font-medium">Nenhuma pauta encontrada</p>
                      <p className="text-sm">Tente ajustar os filtros ou gerar novas pautas.</p>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredPautas.map((pauta) => (
                  <tr key={pauta.ID} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-semibold text-slate-900">{pauta.Tema}</div>
                      <div className="text-xs text-slate-500 mt-0.5">{pauta.Categoria} • {pauta["Posicao no funil"] || "Sem funil"}</div>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-600">{pauta["Palavra-chave principal"] || "-"}</td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-slate-700">{pauta["Produto sugerido"] || "-"}</div>
                      <div className="text-xs text-slate-500">{pauta["CTA sugerido"] || ""}</div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={clsx("inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium", statusStyles[pauta.Status] || "bg-slate-100 text-slate-700 border-slate-200")}>
                        {pauta.Status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end gap-2">
                        {pauta.Status === "Pendente" && (
                          <button
                            onClick={() => handleGenerateArticle(pauta.ID)}
                            disabled={generatingArticleId === pauta.ID}
                            className="inline-flex items-center gap-2 rounded-lg bg-amber-500 px-3 py-2 text-xs font-medium text-white hover:bg-amber-600 disabled:cursor-not-allowed disabled:opacity-60"
                          >
                            {generatingArticleId === pauta.ID ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                            <span>Gerar Artigo</span>
                          </button>
                        )}
                        {canReview(pauta.Status) && (
                          <Link
                            href={`/pautas/${pauta.ID}/review`}
                            className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50"
                          >
                            {pauta.Status === "Publicado" ? <CheckCircle2 className="h-4 w-4 text-green-600" /> : pauta.Status === "Rascunho" ? <Clock3 className="h-4 w-4 text-blue-600" /> : <Eye className="h-4 w-4 text-slate-500" />}
                            <span>{pauta.Status === "Publicado" ? "Ver Publicado" : "Revisar"}</span>
                          </Link>
                        )}
                        {pauta["URL WordPress"] && (
                          <a
                            href={pauta["URL WordPress"]}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50"
                          >
                            <FileText className="h-4 w-4" />
                            <span>WP</span>
                          </a>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
