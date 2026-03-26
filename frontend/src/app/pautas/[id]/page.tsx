"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import PautaForm from "@/components/PautaForm";
import api from "@/lib/api";
import { toast } from "react-hot-toast";

interface EditPautaPageProps {
  params: Promise<{ id: string }>;
}

export default function EditPautaPage({ params }: EditPautaPageProps) {
  const router = useRouter();
  const { id } = use(params);
  const [initialData, setInitialData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);

  useEffect(() => {
    async function fetchPauta() {
      try {
        const response = await api.get(`/pautas/${id}`);
        setInitialData(response.data);
      } catch (error) {
        toast.error("Erro ao buscar dados da pauta");
        router.push("/pautas");
      } finally {
        setFetching(false);
      }
    }
    fetchPauta();
  }, [id, router]);

  const handleSubmit = async (data: any) => {
    setLoading(true);
    try {
      await api.put(`/pautas/${id}`, data);
      toast.success("Pauta atualizada com sucesso!");
      router.push("/pautas");
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Erro ao salvar pauta");
    } finally {
      setLoading(false);
    }
  };

  if (fetching) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-green-600 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <PautaForm 
        title={`Editar Pauta: ${initialData?.tema}`}
        initialData={initialData}
        onSubmit={handleSubmit}
        loading={loading}
      />
    </div>
  );
}
