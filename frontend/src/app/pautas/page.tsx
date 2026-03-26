"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { 
  Search, 
  Edit2, 
  Copy, 
  Archive, 
  Trash2, 
  AlertCircle, 
  Plus, 
  Download,
  Filter,
  Eye,
  Sparkles,
  Loader2
} from "lucide-react";
import api from "@/lib/api";
import clsx from "clsx";
import { toast } from "react-hot-toast";

export default function PautasPage() {
  const [pautas, setPautas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [areaFilter, setAreaFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");

  const fetchPautas = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (search) params.query = search;
      if (statusFilter) params.status = statusFilter;
      if (areaFilter) params.area = areaFilter;
      if (priorityFilter) params.prioridade = priorityFilter;

      const response = await api.get("/pautas/", { params });
      setPautas(response.data);
    } catch (error) {
      console.error("Erro ao buscar pautas:", error);
      toast.error("Erro ao carregar pautas");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchPautas();
    }, 300);
    return () => clearTimeout(timer);
  }, [search, statusFilter, areaFilter, priorityFilter]);

  const handleDuplicate = async (id: number) => {
    try {
      await api.post(`/pautas/${id}/duplicate`);
      toast.success("Pauta duplicada com sucesso");
      fetchPautas();
    } catch (error) {
      toast.error("Erro ao duplicar pauta");
    }
  };

  const handleArchive = async (id: number) => {
    try {
      await api.post(`/pautas/${id}/archive`);
      toast.success("Pauta arquivada");
      fetchPautas();
    } catch (error) {
      toast.error("Erro ao arquivar pauta");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Tem certeza que deseja excluir esta pauta?")) return;
    try {
      await api.delete(`/pautas/${id}`);
      toast.success("Pauta excluída");
      fetchPautas();
    } catch (error) {
      toast.error("Erro ao excluir pauta");
    }
  };

  const handleGenerate = async (id: number) => {
    const toastId = toast.loading("Gerando artigo com IA...");
    try {
      await api.post(`/generation/${id}/generate`);
      toast.success("Artigo gerado com sucesso!", { id: toastId });
      fetchPautas();
    } catch (error: any) {
      console.error("Erro ao gerar:", error);
      toast.error(error.response?.data?.detail || "Erro na geração do artigo.", { id: toastId });
      fetchPautas();
    }
  };

  const statusColors: any = {
    pendente: "bg-slate-100 text-slate-700",
    gerada: "bg-orange-100 text-orange-700",
    publicada: "bg-green-100 text-green-700",
    arquivada: "bg-gray-200 text-gray-600",
    erro: "bg-red-100 text-red-700",
  };

  const priorityColors: any = {
    alta: "text-red-600 font-bold",
    media: "text-orange-500 font-semibold",
    baixa: "text-slate-500",
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Gerenciamento de Pautas</h2>
          <p className="text-sm text-slate-500">Crie, edite e acompanhe o fluxo de produção de conteúdo.</p>
        </div>
        <div className="flex gap-3">
          <a 
            href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/pautas/export/excel`}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            <Download className="h-4 w-4" />
            Exportar Excel
          </a>
          <Link 
            href="/pautas/nova"
            className="inline-flex items-center gap-2 rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 shadow-sm transition-all"
          >
            <Plus className="h-4 w-4" />
            Nova Pauta
          </Link>
        </div>
      </div>

      {/* Filtros Avançados */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div className="relative col-span-1 md:col-span-1">
          <label className="text-xs font-semibold text-slate-500 uppercase mb-1 block">Busca</label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Tema ou palavra-chave..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50 focus:outline-none focus:ring-2 focus:ring-green-500 transition-all"
            />
          </div>
        </div>

        <div>
          <label className="text-xs font-semibold text-slate-500 uppercase mb-1 block">Área</label>
          <select
            value={areaFilter}
            onChange={(e) => setAreaFilter(e.target.value)}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Todas as áreas</option>
            <option value="medicina">Medicina</option>
            <option value="saude">Saúde</option>
            <option value="bem-estar">Bem-estar</option>
          </select>
        </div>

        <div>
          <label className="text-xs font-semibold text-slate-500 uppercase mb-1 block">Prioridade</label>
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Todas as prioridades</option>
            <option value="alta">Alta</option>
            <option value="media">Média</option>
            <option value="baixa">Baixa</option>
          </select>
        </div>

        <div>
          <label className="text-xs font-semibold text-slate-500 uppercase mb-1 block">Status</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Todos os status</option>
            <option value="pendente">Pendente</option>
            <option value="gerada">Gerada</option>
            <option value="publicada">Publicada</option>
            <option value="arquivada">Arquivada</option>
            <option value="erro">Erro</option>
          </select>
        </div>
      </div>

      {/* Tabela de Pautas */}
      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50 text-xs font-semibold uppercase text-slate-500">
                <th className="px-6 py-4">Tema / Área</th>
                <th className="px-6 py-4">Prioridade</th>
                <th className="px-6 py-4">Palavra-chave</th>
                <th className="px-6 py-4 text-center">Status</th>
                <th className="px-6 py-4 text-right">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm text-slate-700">
              {loading ? (
                [1, 2, 3, 4, 5].map((i) => (
                  <tr key={i} className="animate-pulse">
                    <td className="px-6 py-4"><div className="h-4 w-48 bg-slate-100 rounded mb-2" /><div className="h-3 w-24 bg-slate-50 rounded" /></td>
                    <td className="px-6 py-4"><div className="h-4 w-16 bg-slate-100 rounded" /></td>
                    <td className="px-6 py-4"><div className="h-4 w-32 bg-slate-100 rounded" /></td>
                    <td className="px-6 py-4"><div className="h-6 w-20 bg-slate-100 rounded-full mx-auto" /></td>
                    <td className="px-6 py-4"><div className="h-8 w-24 bg-slate-100 ml-auto rounded" /></td>
                  </tr>
                ))
              ) : pautas.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center">
                    <div className="flex flex-col items-center justify-center text-slate-400">
                      <Filter className="h-12 w-12 mb-4 opacity-20" />
                      <p className="text-lg font-medium">Nenhuma pauta encontrada</p>
                      <p className="text-sm">Tente ajustar seus filtros de busca.</p>
                    </div>
                  </td>
                </tr>
              ) : (
                pautas.map((pauta: any) => (
                  <tr key={pauta.id} className="hover:bg-slate-50/50 transition-colors group">
                    <td className="px-6 py-4">
                      <div className="font-semibold text-slate-900 group-hover:text-green-700 transition-colors">{pauta.tema}</div>
                      <div className="text-xs text-slate-500 mt-0.5">{pauta.area || "Sem área"} • {pauta.subarea || "Sem subárea"}</div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={clsx("text-xs uppercase", priorityColors[pauta.prioridade?.toLowerCase()] || "text-slate-400")}>
                        {pauta.prioridade || "N/A"}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-slate-600">
                      {pauta.palavra_chave_principal || "-"}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={clsx("inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize border", statusColors[pauta.status] || "bg-slate-100 text-slate-700")}>
                        {pauta.status}
                      </span>
                      {pauta.error_message && (
                        <span className="inline-flex ml-1 cursor-help" title={pauta.error_message}>
                          <AlertCircle className="h-4 w-4 text-red-500" />
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        {pauta.status === "pendente" && (
                          <button 
                            onClick={() => handleGenerate(pauta.id)}
                            title="Gerar Artigo com IA"
                            className="p-1.5 text-orange-500 hover:bg-orange-50 rounded-lg transition-all"
                          >
                            <Sparkles className="h-4 w-4" />
                          </button>
                        )}
                        {(pauta.status === "gerada" || pauta.status === "publicada") && (
                          <Link 
                            href={`/pautas/${pauta.id}/review`} 
                            title="Revisar e Publicar"
                            className="p-1.5 text-blue-500 hover:bg-blue-50 rounded-lg transition-all"
                          >
                            <Eye className="h-4 w-4" />
                          </Link>
                        )}
                        <Link 
                          href={`/pautas/${pauta.id}`} 
                          title="Editar Pauta"
                          className="p-1.5 text-slate-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-all"
                        >
                          <Edit2 className="h-4 w-4" />
                        </Link>
                        <button 
                          onClick={() => handleDuplicate(pauta.id)}
                          title="Duplicar"
                          className="p-1.5 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all"
                        >
                          <Copy className="h-4 w-4" />
                        </button>
                        <button 
                          onClick={() => handleArchive(pauta.id)}
                          title="Arquivar"
                          className="p-1.5 text-slate-400 hover:text-orange-600 hover:bg-orange-50 rounded-lg transition-all"
                        >
                          <Archive className="h-4 w-4" />
                        </button>
                        <button 
                          onClick={() => handleDelete(pauta.id)}
                          title="Excluir"
                          className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
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
