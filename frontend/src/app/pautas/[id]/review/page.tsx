"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { 
  ArrowLeft, 
  Globe, 
  Calendar, 
  Tag, 
  Layout, 
  Search, 
  CheckCircle, 
  Clock,
  ExternalLink,
  ChevronRight
} from "lucide-react";
import Link from "next/link";
import api from "@/lib/api";
import toast from "react-hot-toast";

interface ReviewPageProps {
  params: Promise<{ id: string }>;
}

export default function ReviewPage({ params }: ReviewPageProps) {
  const { id } = use(params);
  const router = useRouter();
  
  const [pauta, setPauta] = useState<any>(null);
  const [draft, setDraft] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [publishing, setPublishing] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        const [pautaRes, draftRes] = await Promise.all([
          api.get(`/pautas/${id}`),
          api.get(`/generation/${id}/draft`)
        ]);
        setPauta(pautaRes.data);
        setDraft(draftRes.data);
      } catch (error) {
        console.error("Erro ao buscar dados:", error);
        toast.error("Não foi possível carregar o rascunho.");
        router.push("/pautas");
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [id, router]);

  const handlePublish = async () => {
    setPublishing(true);
    const toastId = toast.loading("Enviando artigo para o WordPress...");
    try {
      const response = await api.post(`/wordpress/${id}/publish`);
      toast.success(response.data.message || "Publicado com sucesso!", { id: toastId });
      
      // Redirecionar para a listagem ou para o post
      if (response.data.url) {
        window.open(response.data.url, "_blank");
      }
      router.push("/pautas");
    } catch (error: any) {
      console.error("Erro ao publicar:", error);
      toast.error(error.response?.data?.detail || "Erro ao publicar no WordPress.", { id: toastId });
    } finally {
      setPublishing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-green-500 border-t-transparent"></div>
      </div>
    );
  }

  const isFuture = pauta?.data_planejada && new Date(pauta.data_planejada) > new Date();
  const formattedDate = pauta?.data_planejada ? new Date(pauta.data_planejada).toLocaleString('pt-BR') : null;

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-20">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/pautas" className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
            <ArrowLeft className="h-5 w-5 text-slate-500" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Revisão do Artigo</h1>
            <p className="text-sm text-slate-500">Confira o conteúdo gerado antes de enviar ao WordPress</p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={handlePublish}
            disabled={publishing}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-xl font-semibold text-white shadow-lg transition-all
              ${isFuture 
                ? 'bg-blue-600 hover:bg-blue-700 shadow-blue-200' 
                : 'bg-green-600 hover:bg-green-700 shadow-green-200'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {publishing ? (
              <Clock className="h-5 w-5 animate-spin" />
            ) : isFuture ? (
              <Calendar className="h-5 w-5" />
            ) : (
              <Globe className="h-5 w-5" />
            )}
            <span>{isFuture ? "Agendar no WordPress" : "Publicar no WordPress"}</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lado Esquerdo: Conteúdo Principal */}
        <div className="lg:col-span-2 space-y-6">
          {/* Preview do Artigo */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-6 border-b border-slate-100 bg-slate-50/50 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Layout className="h-5 w-5 text-green-600" />
                <span className="font-semibold text-slate-700">Conteúdo Final</span>
              </div>
              <span className="text-xs bg-white px-2 py-1 rounded border border-slate-200 text-slate-500">HTML Semântico</span>
            </div>
            
            <div className="p-8 prose prose-slate max-w-none">
              <h2 className="text-3xl font-bold text-slate-900 mb-6">{draft?.human_title || draft?.seo_title}</h2>
              {draft?.article_html ? (
                <div dangerouslySetInnerHTML={{ __html: draft.article_html }} />
              ) : (
                <p className="text-slate-400 italic">Nenhum conteúdo gerado.</p>
              )}
            </div>
          </div>
        </div>

        {/* Lado Direito: Sidebar de SEO e Configs */}
        <div className="space-y-6">
          {/* Card de SEO / Yoast */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
            <div className="flex items-center gap-2 mb-2">
              <Search className="h-5 w-5 text-purple-600" />
              <h3 className="font-bold text-slate-900">SEO (Yoast)</h3>
            </div>
            
            <div className="space-y-3">
              <div>
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Título SEO</label>
                <div className="text-sm font-medium text-slate-700 mt-1 line-clamp-2">
                   {draft?.meta_title || draft?.human_title}
                </div>
              </div>
              
              <div>
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Meta Descrição</label>
                <div className="text-sm text-slate-600 mt-1 line-clamp-3">
                   {draft?.meta_description || draft?.excerpt}
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Palavra-Chave Foco</label>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs bg-purple-50 text-purple-700 px-2 py-1 rounded-full border border-purple-100 font-medium">
                    {pauta?.palavra_chave_principal}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Card de Agendamento */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="h-5 w-5 text-blue-600" />
              <h3 className="font-bold text-slate-900">Agendamento</h3>
            </div>
            
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 flex items-start gap-3">
              {isFuture ? (
                <>
                  <Calendar className="h-5 w-5 text-blue-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-bold text-slate-900">Post Agendado</p>
                    <p className="text-xs text-slate-500">{formattedDate}</p>
                  </div>
                </>
              ) : (
                <>
                  <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-bold text-slate-900">Publicação Imediata</p>
                    <p className="text-xs text-slate-500">O post entrará como ativo agora.</p>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Card de Categorias e Tags */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
             <div className="flex items-center gap-2 mb-2">
              <Tag className="h-5 w-5 text-orange-500" />
              <h3 className="font-bold text-slate-900">Taxonomia</h3>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Categoria</label>
                <p className="text-sm font-medium text-slate-700 mt-1">{pauta?.categoria_wordpress || pauta?.area}</p>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider">Tags</label>
                <div className="flex flex-wrap gap-2 mt-1">
                  {pauta?.tags_wordpress?.split(",").map((tag: string) => (
                    <span key={tag} className="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded border border-slate-200">
                      {tag.trim()}
                    </span>
                  )) || <span className="text-xs text-slate-400 italic">Nenhuma tag definida</span>}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
