"use client";

import { useState } from "react";
import { UploadCloud, CheckCircle2, XCircle, AlertCircle } from "lucide-react";
import api from "@/lib/api";

export default function ImportPage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResponse(null);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await api.post("/pautas/import", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      setResponse(res.data);
      setFile(null); // Limpar arquivo após sucesso
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erro ao fazer upload do arquivo.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Importar Planilha de Pautas</h2>
        <p className="text-sm text-slate-500">Envie um arquivo .xlsx para adicionar pautas ao sistema.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="flex items-center justify-center w-full">
          <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-slate-300 border-dashed rounded-xl cursor-pointer bg-white hover:bg-slate-50 transition-colors">
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              <UploadCloud className="w-12 h-12 text-slate-400 mb-4" />
              <p className="mb-2 text-sm text-slate-500">
                <span className="font-semibold">Clique para fazer upload</span> ou arraste e solte
              </p>
              <p className="text-xs text-slate-400">Apenas arquivos .xlsx (Excel)</p>
            </div>
            <input 
              type="file" 
              className="hidden" 
              accept=".xlsx" 
              onChange={handleFileChange} 
            />
          </label>
        </div>

        {file && (
          <div className="flex items-center justify-between p-4 bg-white border border-slate-200 rounded-lg shadow-sm">
            <span className="text-sm font-medium text-slate-700">{file.name}</span>
            <button 
              type="button" 
              onClick={() => setFile(null)}
              className="text-slate-400 hover:text-slate-600"
            >
              <XCircle className="w-5 h-5" />
            </button>
          </div>
        )}

        <button
          type="submit"
          disabled={!file || loading}
          className="w-full flex items-center justify-center gap-2 rounded-lg bg-green-600 px-4 py-3 text-sm font-semibold text-white hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Processando..." : "Importar Pautas"}
        </button>
      </form>

      {/* Resultado do Upload */}
      {response && (
        <div className="rounded-xl border border-green-200 bg-green-50 p-6 space-y-4">
          <div className="flex items-center gap-2 text-green-700 font-semibold">
            <CheckCircle2 className="w-5 h-5" />
            <span>{response.message}</span>
          </div>

          {response.errors && response.errors.length > 0 && (
            <div className="bg-white border border-red-200 rounded-lg p-4 space-y-2">
              <div className="flex items-center gap-2 text-red-600 font-medium text-sm">
                <AlertCircle className="w-4 h-4" />
                <span>Erros encontrados ({response.errors.length}):</span>
              </div>
              <ul className="text-xs text-red-500 list-disc pl-5 space-y-1">
                {response.errors.map((err: any, idx: number) => (
                  <li key={idx}>Linha {err.line}: {err.error}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
          <AlertCircle className="w-5 h-5" />
          <span className="text-sm font-medium">{error}</span>
        </div>
      )}
    </div>
  );
}
