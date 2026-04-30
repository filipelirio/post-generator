"use client";

import { useEffect, useMemo, useState, use } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowLeft,
  ExternalLink,
  Globe,
  Image as ImageIcon,
  Layout,
  Link2,
  Rocket,
  Search,
  Tag,
} from "lucide-react";
import Link from "next/link";
import toast from "react-hot-toast";

import api from "@/lib/api";

interface ReviewPageProps {
  params: Promise<{ id: string }>;
}

type Pauta = {
  ID: string;
  Status: string;
  Tema: string;
  Categoria: string;
  "Palavra-chave principal": string;
  "CTA sugerido": string;
  "Produto sugerido": string;
  "URL WordPress": string;
};

type ArticleDetail = {
  slug: string;
  pauta_id: string;
  title: string;
  category: string;
  content_html: string;
  seo_title: string;
  meta_desc: string;
  focus_kw: string;
  tags: string[];
  internal_links: string[];
  external_links: string[];
  product_mentions: string[];
  image: {
    type: string;
    path: string;
    url: string;
    alt: string;
    prompt: string;
    short_theme: string;
  };
};

export default function ReviewPage({ params }: ReviewPageProps) {
  const { id } = use(params);
  const router = useRouter();

  const [pauta, setPauta] = useState<Pauta | null>(null);
  const [article, setArticle] = useState<ArticleDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [publishingMode, setPublishingMode] = useState<"draft" | "publish" | null>(null);
  const [imagePreviewError, setImagePreviewError] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        const [pautaRes, articleRes] = await Promise.all([
          api.get(`/editorial/pautas/${id}`),
          api.get(`/editorial/articles/${id}`),
        ]);
        setPauta(pautaRes.data);
        setArticle(articleRes.data);
        setImagePreviewError(false);
      } catch (error) {
        console.error("Erro ao buscar dados editoriais:", error);
        toast.error("Nao foi possivel carregar o artigo gerado.");
        router.push("/pautas");
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [id, router]);

  const imagePreviewUrl = useMemo(() => {
    if (!article?.image?.path) return null;
    return `${api.defaults.baseURL}/editorial/articles/${id}/image`;
  }, [article?.image?.path, id]);

  const handlePublish = async (publishStatus: "draft" | "publish") => {
    if (!article) return;

    setPublishingMode(publishStatus);
    const toastId = toast.loading(
      publishStatus === "publish"
        ? "Publicando artigo no WordPress..."
        : "Enviando rascunho para o WordPress..."
    );

    try {
      const response = await api.post("/editorial/articles/publish", {
        pauta_id: id,
        slug: article.slug,
        publish_status: publishStatus,
      });

      toast.success(
        response.data.message ||
          (publishStatus === "publish" ? "Artigo publicado com sucesso." : "Rascunho criado com sucesso."),
        { id: toastId }
      );

      if (response.data.url) {
        window.open(response.data.url, "_blank");
      }

      router.push("/pautas");
    } catch (error: any) {
      console.error("Erro ao publicar:", error);
      toast.error(error.response?.data?.detail || "Erro ao publicar no WordPress.", { id: toastId });
    } finally {
      setPublishingMode(null);
    }
  };

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-green-500 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6 pb-20">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="flex items-center gap-4">
          <Link href="/pautas" className="rounded-lg p-2 transition-colors hover:bg-slate-100">
            <ArrowLeft className="h-5 w-5 text-slate-500" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Revisao editorial</h1>
            <p className="text-sm text-slate-500">
              Previa do artigo, SEO, links e capa antes de seguir para rascunho ou publicacao final.
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => handlePublish("draft")}
            disabled={publishingMode !== null || !article}
            className="flex items-center gap-2 rounded-xl bg-green-600 px-5 py-2.5 font-semibold text-white shadow-lg shadow-green-200 transition hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Globe className={`h-5 w-5 ${publishingMode === "draft" ? "animate-pulse" : ""}`} />
            <span>{publishingMode === "draft" ? "Criando rascunho..." : "Criar rascunho"}</span>
          </button>

          <button
            onClick={() => handlePublish("publish")}
            disabled={publishingMode !== null || !article}
            className="flex items-center gap-2 rounded-xl bg-slate-900 px-5 py-2.5 font-semibold text-white shadow-lg shadow-slate-200 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Rocket className={`h-5 w-5 ${publishingMode === "publish" ? "animate-pulse" : ""}`} />
            <span>{publishingMode === "publish" ? "Publicando agora..." : "Publicar de verdade"}</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50/50 p-6">
              <div className="flex items-center gap-2">
                <Layout className="h-5 w-5 text-green-600" />
                <span className="font-semibold text-slate-700">Previa do artigo</span>
              </div>
              <span className="rounded border border-slate-200 bg-white px-2 py-1 text-xs text-slate-500">HTML SEO</span>
            </div>

            <div className="prose prose-slate max-w-none p-8">
              <h2 className="mb-6 text-3xl font-bold text-slate-900">{article?.title}</h2>
              {article?.content_html ? (
                <div dangerouslySetInnerHTML={{ __html: article.content_html }} />
              ) : (
                <p className="italic text-slate-400">Nenhum conteudo gerado.</p>
              )}
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-2 flex items-center gap-2">
              <Search className="h-5 w-5 text-purple-600" />
              <h3 className="font-bold text-slate-900">SEO (Yoast)</h3>
            </div>

            <div className="space-y-3">
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Titulo SEO</label>
                <div className="mt-1 text-sm font-medium text-slate-700">{article?.seo_title}</div>
              </div>

              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Meta description</label>
                <div className="mt-1 text-sm text-slate-600">{article?.meta_desc}</div>
              </div>

              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Palavra-chave foco</label>
                <div className="mt-1 inline-flex rounded-full border border-purple-100 bg-purple-50 px-2 py-1 text-xs font-medium text-purple-700">
                  {article?.focus_kw}
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-2 flex items-center gap-2">
              <Tag className="h-5 w-5 text-orange-500" />
              <h3 className="font-bold text-slate-900">Pauta e conversao</h3>
            </div>

            <div className="space-y-3 text-sm text-slate-700">
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Tema</label>
                <p className="mt-1">{pauta?.Tema}</p>
              </div>
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Produto sugerido</label>
                <p className="mt-1">{pauta?.["Produto sugerido"] || "-"}</p>
              </div>
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400">CTA sugerido</label>
                <p className="mt-1">{pauta?.["CTA sugerido"] || "-"}</p>
              </div>
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Tags</label>
                <div className="mt-2 flex flex-wrap gap-2">
                  {article?.tags?.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full border border-slate-200 bg-slate-50 px-2 py-1 text-[11px] text-slate-600"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
              {pauta?.["URL WordPress"] ? (
                <div>
                  <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Ultima URL registrada</label>
                  <p className="mt-1 break-all text-slate-600">{pauta["URL WordPress"]}</p>
                </div>
              ) : null}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-2 flex items-center gap-2">
              <Link2 className="h-5 w-5 text-blue-600" />
              <h3 className="font-bold text-slate-900">Links SEO</h3>
            </div>

            <div className="space-y-4 text-sm text-slate-700">
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Internos</label>
                <ul className="mt-2 space-y-2">
                  {article?.internal_links?.map((item) => (
                    <li key={item} className="flex items-start gap-2">
                      <ExternalLink className="mt-0.5 h-3.5 w-3.5 text-slate-400" />
                      <span className="break-all">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Externos</label>
                <ul className="mt-2 space-y-2">
                  {article?.external_links?.map((item) => (
                    <li key={item} className="flex items-start gap-2">
                      <ExternalLink className="mt-0.5 h-3.5 w-3.5 text-slate-400" />
                      <span className="break-all">{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-2 flex items-center gap-2">
              <ImageIcon className="h-5 w-5 text-emerald-600" />
              <h3 className="font-bold text-slate-900">Capa</h3>
            </div>

            <div className="space-y-4 text-sm text-slate-700">
              {imagePreviewUrl && !imagePreviewError ? (
                <div className="overflow-hidden rounded-2xl border border-slate-200 bg-slate-50">
                  <img
                    src={imagePreviewUrl}
                    alt={article?.image?.alt || article?.title || "Capa gerada"}
                    className="h-auto w-full object-cover"
                    onError={() => setImagePreviewError(true)}
                  />
                </div>
              ) : (
                <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-4 py-8 text-center text-slate-500">
                  A previa da capa nao esta disponivel nesta pauta.
                </div>
              )}

              <div className="space-y-2">
                <p><strong>Tipo:</strong> {article?.image?.type || "-"}</p>
                <p className="break-all"><strong>Arquivo:</strong> {article?.image?.path || "Nao gerado"}</p>
                <p><strong>Alt:</strong> {article?.image?.alt || "-"}</p>
                {article?.image?.short_theme ? <p><strong>Tema curto:</strong> {article.image.short_theme}</p> : null}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
