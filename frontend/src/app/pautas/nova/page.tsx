"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import PautaForm from "@/components/PautaForm";
import api from "@/lib/api";
import { toast } from "react-hot-toast";

export default function NovaPautaPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (data: any) => {
    setLoading(true);
    try {
      await api.post("/pautas/", data);
      toast.success("Pauta criada com sucesso!");
      router.push("/pautas");
    } catch (error: any) {
      console.error("Erro ao criar pauta:", error);
      toast.error(error.response?.data?.detail || "Erro ao criar pauta");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <PautaForm 
        title="Criar Nova Pauta"
        onSubmit={handleSubmit}
        loading={loading}
      />
    </div>
  );
}
