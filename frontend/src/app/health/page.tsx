"use client";

import { useCallback, useEffect, useState } from "react";
import { CheckCircle, FileSpreadsheet, FolderArchive, Globe, Image as ImageIcon, Loader2, RefreshCw, Search, Sparkles, XCircle } from "lucide-react";
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
  cron_enabled: boolean;
  cron_mode: "generate_only" | "draft" | "publish";
  cron_dry_run: boolean;
  cron_max_items: number;
  cron_schedule: string;
  cron_allow_unreviewed_publish: boolean;
};

function StatusBadge({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span className={clsx("inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold", ok ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700")}>
      {ok ? <CheckCircle className="h-3.5 w-3.5" /> : <XCircle className="h-3.5 w-3.5" />}
      {label}
    </span>
  );
}

export default function HealthPage() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadStatus = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get<SystemStatus>("/editorial/system/status");
      setStatus(response.data);
      setError(null);
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "Não foi possível carregar a saúde do motor editorial."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadStatus();
  }, [loadStatus]);

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Saúde do motor</h2>
          <p className="mt-1 text-sm text-slate-500">Diagnóstico das integrações, automação, armazenamento e backups.</p>
        </div>
        <button onClick={loadStatus} disabled={loading} className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:opacity-50">
          <RefreshCw className={clsx("h-4 w-4", loading && "animate-spin")} />
          Atualizar
        </button>
      </div>

      {loading && !status ? (
        <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-8 text-sm text-slate-500 shadow-sm">
          <Loader2 className="h-4 w-4 animate-spin" />
          Verificando integrações...
        </div>
      ) : null}
      {error ? <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm font-medium text-rose-700">{error}</div> : null}

      {status ? (
        <>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            {[
              { icon: Sparkles, color: "text-violet-600", title: "GPT editorial", ok: status.openai_configured, label: status.openai_configured ? "Configurado" : "Pendente" },
              { icon: Search, color: "text-blue-600", title: "Web search", ok: status.websearch_enabled, label: status.websearch_enabled ? "Ativo" : "Desligado" },
              { icon: ImageIcon, color: "text-emerald-600", title: "Capas IA", ok: status.image_generation_enabled, label: status.image_generation_enabled ? "Prontas" : "Indisponíveis" },
              { icon: Globe, color: "text-green-600", title: "WordPress", ok: status.wordpress_connection_ok, label: status.wordpress_connection_ok ? "Conectado" : "Verificar" },
            ].map(({ icon: Icon, color, title, ok, label }) => (
              <div key={title} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                <div className="mb-3 flex items-center gap-2">
                  <Icon className={`h-5 w-5 ${color}`} />
                  <span className="font-semibold text-slate-800">{title}</span>
                </div>
                <StatusBadge ok={ok} label={label} />
              </div>
            ))}
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="text-lg font-bold text-slate-900">Automação programada</h3>
              <StatusBadge ok={status.cron_enabled} label={status.cron_enabled ? "Ativa" : "Inativa"} />
              <dl className="mt-5 grid grid-cols-2 gap-4 text-sm">
                <div><dt className="text-slate-500">Frequência</dt><dd className="mt-1 font-mono font-semibold text-slate-800">{status.cron_schedule}</dd></div>
                <div><dt className="text-slate-500">Modo</dt><dd className="mt-1 font-semibold text-slate-800">{status.cron_mode}</dd></div>
                <div><dt className="text-slate-500">Itens por ciclo</dt><dd className="mt-1 font-semibold text-slate-800">{status.cron_max_items}</dd></div>
                <div><dt className="text-slate-500">Execução</dt><dd className="mt-1 font-semibold text-slate-800">{status.cron_dry_run ? "Simulação" : "Real"}</dd></div>
              </dl>
              {status.cron_mode === "publish" && status.cron_allow_unreviewed_publish ? (
                <p className="mt-4 rounded-xl bg-rose-50 p-3 text-sm font-medium text-rose-800">Publicação direta sem revisão está habilitada.</p>
              ) : null}
            </section>

            <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex items-center gap-2">
                <FolderArchive className="h-5 w-5 text-amber-600" />
                <h3 className="text-lg font-bold text-slate-900">Arquivos e backups</h3>
              </div>
              {[
                ["Planilha editorial", status.excel_path, FileSpreadsheet],
                ["Artigos gerados", status.generated_articles_dir, FileSpreadsheet],
                ["Capas geradas", status.generated_images_dir, ImageIcon],
                ["Backups", status.backups_dir, FolderArchive],
              ].map(([label, path, Icon]) => {
                const ItemIcon = Icon as typeof FileSpreadsheet;
                return (
                  <div key={label as string} className="mb-3 flex gap-3 rounded-xl bg-slate-50 p-3 last:mb-0">
                    <ItemIcon className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />
                    <div className="min-w-0">
                      <p className="text-xs font-semibold uppercase text-slate-500">{label as string}</p>
                      <p className="break-all text-sm text-slate-700">{path as string}</p>
                    </div>
                  </div>
                );
              })}
            </section>
          </div>

          <p className="rounded-2xl border border-blue-100 bg-blue-50 p-4 text-sm text-blue-800">
            A frequência exibida é a política configurada no app; na VPS, confirme que o `crontab` usa a mesma expressão para executar `backend/scripts/run_cron.py`.
          </p>
        </>
      ) : null}
    </div>
  );
}
