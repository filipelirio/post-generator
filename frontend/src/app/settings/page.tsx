"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { ChevronDown, KeyRound, Loader2, Save, ShieldAlert, SlidersHorizontal } from "lucide-react";
import { toast } from "react-hot-toast";

import api, { getApiErrorMessage } from "@/lib/api";

type CronMode = "generate_only" | "draft" | "publish";

type EditorialConfiguration = {
  client_instructions: string;
  seo_guidelines: string;
  prompt_generate_pautas: string;
  prompt_generate_article: string;
  openai_api_key_configured: boolean;
  openai_model: string;
  openai_image_model: string;
  openai_image_size: string;
  openai_image_quality: string;
  openai_websearch_enabled: boolean;
  wordpress_url: string;
  wordpress_username: string;
  wordpress_application_password_configured: boolean;
  cron_enabled: boolean;
  cron_token_configured: boolean;
  cron_mode: CronMode;
  cron_max_items: number;
  cron_schedule: string;
  cron_dry_run: boolean;
  cron_allow_unreviewed_publish: boolean;
};

const inputClassName =
  "mt-1 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-800 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100";

function ConfiguredNote({ configured }: { configured: boolean }) {
  return (
    <span className={`text-xs font-medium ${configured ? "text-emerald-700" : "text-amber-700"}`}>
      {configured ? "Já configurada. Deixe vazio para manter." : "Ainda não configurada."}
    </span>
  );
}

export default function SettingsPage() {
  const [configuration, setConfiguration] = useState<EditorialConfiguration | null>(null);
  const [openaiKey, setOpenaiKey] = useState("");
  const [wordpressPassword, setWordpressPassword] = useState("");
  const [cronToken, setCronToken] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadConfiguration = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get<EditorialConfiguration>("/editorial/configuration");
      setConfiguration(response.data);
      setError(null);
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, "Não foi possível carregar as configurações."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadConfiguration();
  }, [loadConfiguration]);

  const setField = <K extends keyof EditorialConfiguration>(field: K, value: EditorialConfiguration[K]) => {
    setConfiguration((current) => (current ? { ...current, [field]: value } : current));
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!configuration) {
      return;
    }
    setSaving(true);
    const toastId = toast.loading("Salvando configurações...");
    try {
      const response = await api.put("/editorial/configuration", {
        ...configuration,
        openai_api_key: openaiKey || null,
        wordpress_application_password: wordpressPassword || null,
        cron_token: cronToken || null,
      });
      setConfiguration(response.data.configuration);
      setOpenaiKey("");
      setWordpressPassword("");
      setCronToken("");
      toast.success("Configurações atualizadas.", { id: toastId });
    } catch (err: unknown) {
      toast.error(getApiErrorMessage(err, "Erro ao salvar configurações."), { id: toastId });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-8 text-sm text-slate-500 shadow-sm">
        <Loader2 className="h-4 w-4 animate-spin" />
        Carregando configurações do cliente...
      </div>
    );
  }

  if (error || !configuration) {
    return (
      <div className="rounded-2xl border border-rose-200 bg-rose-50 p-5 text-sm font-medium text-rose-700">
        {error || "Configuração indisponível."}
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="mx-auto max-w-6xl space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Configurações do cliente</h2>
          <p className="mt-1 max-w-3xl text-sm text-slate-500">
            Personalize a marca, estratégia editorial, APIs e automação. Assim, o mesmo motor pode operar blogs diferentes sem alterar código.
          </p>
        </div>
        <button
          type="submit"
          disabled={saving}
          className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700 disabled:opacity-60"
        >
          {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
          Salvar configurações
        </button>
      </div>

      <section className="rounded-2xl border border-emerald-100 bg-white p-6 shadow-sm">
        <div className="mb-5 flex items-start gap-3">
          <SlidersHorizontal className="mt-0.5 h-5 w-5 text-emerald-600" />
          <div>
            <h3 className="text-lg font-bold text-slate-900">Identidade e direção editorial</h3>
            <p className="text-sm text-slate-500">
              Estes dois textos são a personalidade do cliente: público, produtos, URLs, tom de voz, limites e critérios de SEO.
            </p>
          </div>
        </div>
        <div className="grid gap-5 lg:grid-cols-2">
          <label className="text-sm font-semibold text-slate-800">
            Instruções do cliente
            <textarea
              value={configuration.client_instructions}
              onChange={(event) => setField("client_instructions", event.target.value)}
              rows={18}
              className={`${inputClassName} resize-y font-mono text-xs leading-relaxed`}
            />
          </label>
          <label className="text-sm font-semibold text-slate-800">
            Diretrizes de SEO
            <textarea
              value={configuration.seo_guidelines}
              onChange={(event) => setField("seo_guidelines", event.target.value)}
              rows={18}
              className={`${inputClassName} resize-y font-mono text-xs leading-relaxed`}
            />
          </label>
        </div>
      </section>

      <details className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <summary className="flex cursor-pointer list-none items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-bold text-slate-900">Templates avançados dos prompts</h3>
            <p className="text-sm text-slate-500">Edite somente para ajustar a lógica geral de pauta ou artigo.</p>
          </div>
          <ChevronDown className="h-5 w-5 text-slate-500" />
        </summary>
        <p className="mt-4 rounded-lg bg-amber-50 p-3 text-sm text-amber-800">
          Os placeholders obrigatórios precisam permanecer nos templates; sem eles a geração perde o contexto do cliente.
        </p>
        <div className="mt-5 grid gap-5 lg:grid-cols-2">
          <label className="text-sm font-semibold text-slate-800">
            Template para pautas
            <textarea
              value={configuration.prompt_generate_pautas}
              onChange={(event) => setField("prompt_generate_pautas", event.target.value)}
              rows={22}
              className={`${inputClassName} resize-y font-mono text-xs leading-relaxed`}
            />
          </label>
          <label className="text-sm font-semibold text-slate-800">
            Template para artigos
            <textarea
              value={configuration.prompt_generate_article}
              onChange={(event) => setField("prompt_generate_article", event.target.value)}
              rows={22}
              className={`${inputClassName} resize-y font-mono text-xs leading-relaxed`}
            />
          </label>
        </div>
      </details>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5 flex items-center gap-2">
            <KeyRound className="h-5 w-5 text-slate-600" />
            <h3 className="text-lg font-bold text-slate-900">OpenAI e geração</h3>
          </div>
          <div className="space-y-4">
            <label className="block text-sm font-semibold text-slate-800">
              Chave da API OpenAI
              <input
                type="password"
                autoComplete="new-password"
                value={openaiKey}
                onChange={(event) => setOpenaiKey(event.target.value)}
                placeholder="Cole uma nova chave apenas para substituir"
                className={inputClassName}
              />
              <ConfiguredNote configured={configuration.openai_api_key_configured} />
            </label>
            <label className="block text-sm font-semibold text-slate-800">
              Modelo de texto
              <input value={configuration.openai_model} onChange={(event) => setField("openai_model", event.target.value)} className={inputClassName} />
            </label>
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block text-sm font-semibold text-slate-800">
                Modelo de imagem
                <input value={configuration.openai_image_model} onChange={(event) => setField("openai_image_model", event.target.value)} className={inputClassName} />
              </label>
              <label className="block text-sm font-semibold text-slate-800">
                Qualidade
                <input value={configuration.openai_image_quality} onChange={(event) => setField("openai_image_quality", event.target.value)} className={inputClassName} />
              </label>
            </div>
            <label className="block text-sm font-semibold text-slate-800">
              Tamanho da imagem
              <input value={configuration.openai_image_size} onChange={(event) => setField("openai_image_size", event.target.value)} className={inputClassName} />
            </label>
            <label className="flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50 p-3 text-sm font-medium text-slate-800">
              <input
                type="checkbox"
                checked={configuration.openai_websearch_enabled}
                onChange={(event) => setField("openai_websearch_enabled", event.target.checked)}
                className="h-4 w-4 accent-emerald-600"
              />
              Usar web search na geração de pautas, links e artigos
            </label>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5 flex items-center gap-2">
            <KeyRound className="h-5 w-5 text-slate-600" />
            <h3 className="text-lg font-bold text-slate-900">WordPress</h3>
          </div>
          <div className="space-y-4">
            <label className="block text-sm font-semibold text-slate-800">
              URL do blog
              <input value={configuration.wordpress_url} onChange={(event) => setField("wordpress_url", event.target.value)} placeholder="https://blog.exemplo.com" className={inputClassName} />
            </label>
            <label className="block text-sm font-semibold text-slate-800">
              Usuário WordPress
              <input value={configuration.wordpress_username} onChange={(event) => setField("wordpress_username", event.target.value)} className={inputClassName} />
            </label>
            <label className="block text-sm font-semibold text-slate-800">
              Application Password
              <input
                type="password"
                autoComplete="new-password"
                value={wordpressPassword}
                onChange={(event) => setWordpressPassword(event.target.value)}
                placeholder="Cole uma nova senha apenas para substituir"
                className={inputClassName}
              />
              <ConfiguredNote configured={configuration.wordpress_application_password_configured} />
            </label>
            <p className="rounded-xl bg-slate-50 p-3 text-sm text-slate-600">
              O WordPress recebe HTML semântico, imagem destacada e metadados Yoast preparados pelo pacote editorial.
            </p>
          </div>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-bold text-slate-900">Automação e cron job da VPS</h3>
        <p className="mt-1 text-sm text-slate-500">
          A aplicação salva a política e a frequência. Na VPS, o cron do sistema operacional deve chamar o script com esta mesma expressão.
        </p>
        <div className="mt-5 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <label className="flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50 p-3 text-sm font-medium text-slate-800">
            <input type="checkbox" checked={configuration.cron_enabled} onChange={(event) => setField("cron_enabled", event.target.checked)} className="h-4 w-4 accent-emerald-600" />
            Cron ativo
          </label>
          <label className="block text-sm font-semibold text-slate-800">
            Modo
            <select value={configuration.cron_mode} onChange={(event) => setField("cron_mode", event.target.value as CronMode)} className={inputClassName}>
              <option value="generate_only">Gerar pacote</option>
              <option value="draft">Criar rascunho</option>
              <option value="publish">Publicar</option>
            </select>
          </label>
          <label className="block text-sm font-semibold text-slate-800">
            Máximo por ciclo
            <input type="number" min={1} max={5} value={configuration.cron_max_items} onChange={(event) => setField("cron_max_items", Number(event.target.value))} className={inputClassName} />
          </label>
          <label className="block text-sm font-semibold text-slate-800">
            Frequência cron
            <input value={configuration.cron_schedule} onChange={(event) => setField("cron_schedule", event.target.value)} placeholder="0 7 * * 1-5" className={`${inputClassName} font-mono`} />
          </label>
        </div>
        <p className="mt-2 text-xs text-slate-500">Exemplo: `0 7 * * 1-5` executa às 07:00, de segunda a sexta-feira.</p>
        <div className="mt-5 grid gap-4 md:grid-cols-3">
          <label className="block text-sm font-semibold text-slate-800">
            Token interno do cron
            <input type="password" autoComplete="new-password" value={cronToken} onChange={(event) => setCronToken(event.target.value)} placeholder="Novo token para substituir" className={inputClassName} />
            <ConfiguredNote configured={configuration.cron_token_configured} />
          </label>
          <label className="flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50 p-3 text-sm font-medium text-slate-800">
            <input type="checkbox" checked={configuration.cron_dry_run} onChange={(event) => setField("cron_dry_run", event.target.checked)} className="h-4 w-4 accent-emerald-600" />
            Somente simulação
          </label>
          <label className="flex items-center gap-3 rounded-xl border border-rose-100 bg-rose-50 p-3 text-sm font-medium text-rose-800">
            <input type="checkbox" checked={configuration.cron_allow_unreviewed_publish} onChange={(event) => setField("cron_allow_unreviewed_publish", event.target.checked)} className="h-4 w-4 accent-rose-600" />
            Permitir publicação sem revisão
          </label>
        </div>
      </section>

      <div className="flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
        <ShieldAlert className="mt-0.5 h-5 w-5 shrink-0" />
        <p>
          Chaves e senhas são gravadas somente no arquivo `.env` local e nunca retornam ao navegador. Ao publicar este painel na VPS, proteja toda a aplicação com autenticação.
        </p>
      </div>
    </form>
  );
}
