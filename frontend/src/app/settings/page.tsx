"use client";

import { useState } from "react";
import { Settings, RefreshCw, CheckCircle, XCircle, Sparkles } from "lucide-react";
import api from "@/lib/api";
import clsx from "clsx";

export default function SettingsPage() {
  const [testing, setTesting] = useState(false);
  const [status, setStatus] = useState<{ type: "success" | "error", message: string } | null>(null);

  const handleTestConnection = async () => {
    setTesting(true);
    setStatus(null);
    try {
      const response = await api.post("/wordpress/test-connection");
      setStatus({ type: "success", message: response.data.message });
    } catch (error: any) {
      setStatus({ 
        type: "error", 
        message: error.response?.data?.detail || "Falha ao conectar com o WordPress." 
      });
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Configurações de Integração</h2>
        <p className="text-sm text-slate-500">Teste a conexão com serviços externos e visualize credenciais.</p>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-6">
        <div className="flex items-center gap-2 border-b pb-4">
          <Settings className="w-5 h-5 text-slate-500" />
          <h3 className="text-lg font-bold text-slate-800">WordPress</h3>
        </div>

        <div className="space-y-4">
          <p className="text-sm text-slate-600">
            As credenciais do WordPress são gerenciadas através do arquivo <code className="bg-slate-100 px-1.5 py-0.5 rounded text-xs">.env</code> no backend para maior segurança.
          </p>

          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-semibold text-slate-500">URL do Blog:</span>
              <p className="text-slate-800 mt-1">https://easymedicina.com</p>
            </div>
            <div>
              <span className="font-semibold text-slate-500">Autenticação:</span>
              <p className="text-slate-800 mt-1">Application Password</p>
            </div>
          </div>

          <button
            onClick={handleTestConnection}
            disabled={testing}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            <RefreshCw className={clsx("h-4 w-4 text-slate-500", testing && "animate-spin")} />
            {testing ? "Testando..." : "Testar Conexão"}
          </button>

          {status && (
            <div className={clsx(
              "flex items-center gap-2 p-3 rounded-lg text-sm font-medium",
              status.type === "success" ? "bg-green-50 text-green-700 border border-green-200" : "bg-red-50 text-red-700 border border-red-200"
            )}>
              {status.type === "success" ? <CheckCircle className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
              <span>{status.message}</span>
            </div>
          )}
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
        <div className="flex items-center gap-2 border-b pb-4">
          <Sparkles className="w-5 h-5 text-slate-500" />
          <h3 className="text-lg font-bold text-slate-800">IA (Gemini)</h3>
        </div>
        <p className="text-sm text-slate-600">
          A integração com o Gemini API utiliza o modelo <code className="bg-slate-100 px-1.5 py-0.5 rounded text-xs">gemini-2.1-flash</code> para geração rápida de plano e artigo.
        </p>
      </div>
    </div>
  );
}
