"use client";

import { useCallback, useEffect, useState } from "react";
import {
  CheckCircle,
  FileSpreadsheet,
  FolderArchive,
  Globe,
  Image as ImageIcon,
  RefreshCw,
  Search,
  Settings,
  Sparkles,
  XCircle,
} from "lucide-react";
import clsx from "clsx";

import api, { getApiErrorMessage } from "@/lib/api";

type SystemStatus = {
  openai_configured: boolean;
  image_generation_enabled: boolean;
  websearch_enabled: boolean;
  wordpress_url: string;
  wordpress_configured: boolean;
  wordpress_connection_ok: boolean;
  excel_path: string;
  generated_articles_dir: string;
  generated_images_dir: string;
  backups_dir: string;
};

function StatusBadge({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold",
        ok ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"
      )}
    >
      {ok ? <CheckCircle className="h-3.5 w-3.5" /> : <XCircle className="h-3.5 w-3.5" />}
      {label}
    </span>
  );
}

export default function SettingsPage() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadStatus = useCallback(async (showRefresh = false) => {
    if (showRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    try {
      const response = await api.get("/editorial/system/status");
      setStatus(response.data);
      setError(null);
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "Não foi possível carregar o diagnóstico do fluxo editorial."));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    loadStatus();
  }, [loadStatus]);

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Configurações do fluxo editorial</h2>
          <p className="mt-1 text-sm text-slate-500">
            Aqui fica o panorama real da operação: GPT com web search, geração de capas, planilha local,
            backups e WordPress.
          </p>
        </div>

        <button
          onClick={() => loadStatus(true)}
          disabled={refreshing}
          className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:opacity-50"
        >
          <RefreshCw className={clsx("h-4 w-4", refreshing && "animate-spin")} />
          {refreshing ? "Atualizando..." : "Atualizar diagnóstico"}
        </button>
      </div>

      {loading ? (
        <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="flex items-center gap-3 text-sm text-slate-500">
            <RefreshCw className="h-4 w-4 animate-spin" />
            Carregando estado da aplicação...
          </div>
        </div>
      ) : null}

      {error ? (
        <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm font-medium text-rose-700">
          {error}
        </div>
      ) : null}

      {status ? (
        <>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="mb-3 flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-violet-600" />
                <span className="font-semibold text-slate-800">GPT editorial</span>
              </div>
              <StatusBadge ok={status.openai_configured} label={status.openai_configured ? "Configurado" : "Pendente"} />
              <p className="mt-3 text-sm text-slate-600">
                O backend esta pronto para gerar pautas e artigos com o fluxo novo.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="mb-3 flex items-center gap-2">
                <Search className="h-5 w-5 text-blue-600" />
                <span className="font-semibold text-slate-800">Web search</span>
              </div>
              <StatusBadge ok={status.websearch_enabled} label={status.websearch_enabled ? "Ativo" : "Desligado"} />
              <p className="mt-3 text-sm text-slate-600">
                O gerador esta orientado a buscar referencias, links internos e links externos reais.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="mb-3 flex items-center gap-2">
                <ImageIcon className="h-5 w-5 text-emerald-600" />
                <span className="font-semibold text-slate-800">Capas IA</span>
              </div>
              <StatusBadge
                ok={status.image_generation_enabled}
                label={status.image_generation_enabled ? "Prontas" : "Indisponíveis"}
              />
              <p className="mt-3 text-sm text-slate-600">
                A capa pode ser gerada junto com o pacote do artigo e enviada ao WordPress.
              </p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="mb-3 flex items-center gap-2">
                <Globe className="h-5 w-5 text-green-600" />
                <span className="font-semibold text-slate-800">WordPress</span>
              </div>
              <StatusBadge
                ok={status.wordpress_connection_ok}
                label={status.wordpress_connection_ok ? "Conectado" : "Verificar"}
              />
              <p className="mt-3 text-sm text-slate-600">
                {status.wordpress_url}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex items-center gap-2">
                <Settings className="h-5 w-5 text-slate-500" />
                <h3 className="text-lg font-bold text-slate-900">Fluxo ativo</h3>
              </div>

              <div className="space-y-4 text-sm text-slate-700">
                <div>
                  <p className="font-semibold text-slate-900">Geração de pautas</p>
                  <p className="mt-1 text-slate-600">
                    O GPT gera novas pautas com base no manual da Easy Medicina, na planilha local e em pesquisa web.
                  </p>
                </div>
                <div>
                  <p className="font-semibold text-slate-900">Geração de artigos</p>
                  <p className="mt-1 text-slate-600">
                    Cada artigo sai com corpo HTML, SEO para Yoast, links internos, links externos, CTA e capa.
                  </p>
                </div>
                <div>
                  <p className="font-semibold text-slate-900">Publicação</p>
                  <p className="mt-1 text-slate-600">
                    A review agora suporta rascunho e publicação direta no WordPress a partir do mesmo pacote.
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex items-center gap-2">
                <FolderArchive className="h-5 w-5 text-amber-600" />
                <h3 className="text-lg font-bold text-slate-900">Arquivos e backups</h3>
              </div>

              <div className="space-y-4 text-sm text-slate-700">
                <div>
                  <p className="font-semibold text-slate-900">Planilha local</p>
                  <p className="mt-1 break-all rounded-lg bg-slate-50 px-3 py-2 text-slate-600">
                    {status.excel_path}
                  </p>
                </div>
                <div>
                  <p className="font-semibold text-slate-900">Pacotes gerados</p>
                  <p className="mt-1 break-all rounded-lg bg-slate-50 px-3 py-2 text-slate-600">
                    {status.generated_articles_dir}
                  </p>
                </div>
                <div>
                  <p className="font-semibold text-slate-900">Capas geradas</p>
                  <p className="mt-1 break-all rounded-lg bg-slate-50 px-3 py-2 text-slate-600">
                    {status.generated_images_dir}
                  </p>
                </div>
                <div>
                  <p className="font-semibold text-slate-900">Backups automáticos</p>
                  <p className="mt-1 break-all rounded-lg bg-amber-50 px-3 py-2 text-amber-700">
                    {status.backups_dir}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <FileSpreadsheet className="h-5 w-5 text-emerald-600" />
              <h3 className="text-lg font-bold text-slate-900">O que está versionado automaticamente</h3>
            </div>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
                <p className="font-semibold text-slate-900">Planilha editorial</p>
                <p className="mt-2 text-sm text-slate-600">
                  Cada escrita da planilha cria um snapshot em backup para manter histórico operacional.
                </p>
              </div>
              <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
                <p className="font-semibold text-slate-900">Pacotes do artigo</p>
                <p className="mt-2 text-sm text-slate-600">
                  Os arquivos de artigo, SEO e imagem são salvos em versões com timestamp.
                </p>
              </div>
              <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
                <p className="font-semibold text-slate-900">Capas geradas</p>
                <p className="mt-2 text-sm text-slate-600">
                  As capas geradas pelo GPT também entram no trilho de backup para reaproveitamento futuro.
                </p>
              </div>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
