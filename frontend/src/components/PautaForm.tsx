"use client";

import { useState, useEffect } from "react";
import { 
  Save, 
  ArrowLeft, 
  ChevronDown, 
  ChevronUp, 
  Info,
  Layers,
  Search,
  PenTool,
  DollarSign,
  Link2,
  Image as ImageIcon,
  Globe
} from "lucide-react";
import Link from "next/link";
import clsx from "clsx";

interface PautaFormProps {
  initialData?: any;
  onSubmit: (data: any) => Promise<void>;
  loading?: boolean;
  title: string;
}

export default function PautaForm({ initialData, onSubmit, loading, title }: PautaFormProps) {
  const [formData, setFormData] = useState<any>({
    tema: "",
    prioridade: "Media",
    status: "pendente",
    ...initialData
  });

  const [activeTab, setActiveTab] = useState("identificacao");

  // Se os dados iniciais mudarem (ex: no edit), atualiza o form
  useEffect(() => {
    if (initialData) {
      setFormData((prev: any) => ({ ...prev, ...initialData }));
    }
  }, [initialData]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev: any) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.tema) {
      alert("O campo 'Tema' é obrigatório.");
      return;
    }
    onSubmit(formData);
  };

  const sections = [
    { id: "identificacao", name: "Identificação", icon: Layers },
    { id: "seo", name: "SEO & Estratégia", icon: Search },
    { id: "estrutura", name: "Estrutura & Redação", icon: PenTool },
    { id: "monetizacao", name: "Conversão", icon: DollarSign },
    { id: "links", name: "Links & Referências", icon: Link2 },
    { id: "imagem", name: "Imagem de Capa", icon: ImageIcon },
    { id: "publicacao", name: "Publicação", icon: Globe },
  ];

  const renderField = (label: string, name: string, type: string = "text", placeholder: string = "", options?: string[]) => {
    const baseClasses = "w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500 transition-all";
    
    return (
      <div className="space-y-1">
        <label className="text-xs font-semibold text-slate-600 uppercase" htmlFor={name}>{label}</label>
        {type === "select" ? (
          <select name={name} id={name} value={formData[name] || ""} onChange={handleChange} className={baseClasses}>
            <option value="">Selecione...</option>
            {options?.map(opt => <option key={opt} value={opt}>{opt}</option>)}
          </select>
        ) : type === "textarea" ? (
          <textarea name={name} id={name} value={formData[name] || ""} onChange={handleChange} placeholder={placeholder} rows={3} className={baseClasses} />
        ) : (
          <input type={type} name={name} id={name} value={formData[name] || ""} onChange={handleChange} placeholder={placeholder} className={baseClasses} />
        )}
      </div>
    );
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="sticky top-0 z-20 flex items-center justify-between border-b border-slate-200 bg-slate-50/95 backdrop-blur py-4 mb-6">
        <div className="flex items-center gap-4">
          <Link href="/pautas" className="p-2 text-slate-400 hover:text-slate-600 hover:bg-white rounded-full transition-all">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <h2 className="text-xl font-bold text-slate-900">{title}</h2>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-lg bg-green-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-green-700 shadow-md transition-all disabled:opacity-50"
        >
          {loading ? "Salvando..." : <><Save className="h-4 w-4" /> Salvar Pauta</>}
        </button>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Navegação Lateral de Seções */}
        <aside className="lg:w-64 flex-shrink-0">
          <nav className="sticky top-24 flex flex-col gap-1">
            {sections.map((sec) => {
              const Icon = sec.icon;
              const isActive = activeTab === sec.id;
              return (
                <button
                  key={sec.id}
                  type="button"
                  onClick={() => setActiveTab(sec.id)}
                  className={clsx(
                    "flex items-center gap-3 px-4 py-3 text-sm font-medium rounded-xl transition-all text-left",
                    isActive 
                      ? "bg-white text-green-700 shadow-sm border border-slate-200" 
                      : "text-slate-500 hover:bg-slate-200/50"
                  )}
                >
                  <Icon className={clsx("h-4 w-4", isActive ? "text-green-600" : "text-slate-400")} />
                  {sec.name}
                </button>
              );
            })}
          </nav>
        </aside>

        {/* Conteúdo do Formulário */}
        <div className="flex-1 bg-white rounded-2xl border border-slate-200 shadow-sm p-8 min-h-[600px]">
          {activeTab === "identificacao" && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
              <div className="border-l-4 border-green-500 pl-4 mb-8">
                <h3 className="text-lg font-bold text-slate-800">Identificação & Classificação</h3>
                <p className="text-sm text-slate-500">Dados fundamentais para organizar sua linha editorial.</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {renderField("Tema (Obrigatório)", "tema", "text", "Sobre o que é o artigo?")}
                {renderField("Prioridade", "prioridade", "select", "", ["Alta", "Media", "Baixa"])}
                {renderField("Área", "area", "select", "", ["Medicina", "Bem-estar", "Saude", "Tecnologia"])}
                {renderField("Subárea", "subarea")}
                {renderField("Categoria Principal", "categoria_principal")}
                {renderField("Título Base (H1 Sugerido)", "titulo_base", "text", "Como você imagina o título?")}
              </div>
            </div>
          )}

          {activeTab === "seo" && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
              <div className="border-l-4 border-blue-500 pl-4 mb-8">
                <h3 className="text-lg font-bold text-slate-800">SEO & Estratégia</h3>
                <p className="text-sm text-slate-500">Direcionais para garantir que o artigo performe no Google.</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {renderField("Palavra-chave Principal", "palavra_chave_principal")}
                {renderField("Palavras-chave Secundárias", "palavras_chave_secundarias", "textarea", "Separadas por vírgula")}
                {renderField("Intenção de Busca", "intencao_de_busca", "select", "", ["Informativa", "Navegação", "Transacional", "Comercial"])}
                {renderField("Público-alvo", "publico_alvo")}
                {renderField("Objetivo do Artigo", "objetivo_do_artigo")}
                {renderField("Estágio do Funil", "estagio_do_funil", "select", "", ["Topo (TOFU)", "Meio (MOFU)", "Fundo (BOFU)"])}
                {renderField("Ângulo SEO", "angulo_seo")}
                {renderField("Pergunta Principal do Usuário", "pergunta_principal_do_usuario")}
              </div>
            </div>
          )}

          {activeTab === "estrutura" && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
              <div className="border-l-4 border-teal-500 pl-4 mb-8">
                <h3 className="text-lg font-bold text-slate-800">Estrutura & Redação</h3>
                <p className="text-sm text-slate-500">Instruções detalhadas para a IA escrever o texto.</p>
              </div>
              <div className="grid grid-cols-1 gap-6">
                {renderField("Resumo da Pauta", "resumo_da_pauta", "textarea")}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {renderField("Tom de Voz", "tom_de_voz")}
                  {renderField("Nível de Profundidade", "nivel_de_profundidade", "select", "", ["Iniciante", "Intermediário", "Avançado", "Especialista"])}
                  {renderField("Formato do Artigo", "formato_do_artigo", "select", "", ["Lista", "Guia Completo", "Notícia", "Review", "Tutorial"])}
                  {renderField("Tamanho Estimado (Palavras)", "tamanho_estimado")}
                </div>
                {renderField("Outline (H2 e H3 sugeridos)", "outline_h2_h3", "textarea")}
                {renderField("Tópicos Obrigatórios", "topicos_obrigatorios", "textarea")}
                {renderField("Tópicos Proibidos", "topicos_proibidos", "textarea")}
                {renderField("Perguntas Frequentes Desejadas (FAQ)", "perguntas_frequentes_desejadas", "textarea")}
                {renderField("Restrições Editoriais", "restricoes_editoriais", "textarea")}
              </div>
            </div>
          )}

          {activeTab === "monetizacao" && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
              <div className="border-l-4 border-orange-500 pl-4 mb-8">
                <h3 className="text-lg font-bold text-slate-800">Conversão & Monetização</h3>
                <p className="text-sm text-slate-500">Como este artigo vai gerar resultado para o negócio.</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {renderField("Objetivo de Conversão", "objetivo_de_conversao")}
                {renderField("Produto Relacionado", "produto_relacionado")}
                {renderField("Serviço Relacionado", "servico_relacionado")}
                {renderField("CTA Principal", "cta_principal")}
                {renderField("CTA Secundário", "cta_secundario")}
                {renderField("Link de Destino CTA", "link_de_destino_cta")}
                {renderField("Bloco Promocional 1", "bloco_promocional_1", "textarea")}
                {renderField("Bloco Promocional 2", "bloco_promocional_2", "textarea")}
                {renderField("Momento do Anúncio", "momento_do_anuncio")}
                {renderField("Tipo de Anúncio", "tipo_de_anuncio")}
              </div>
            </div>
          )}

          {activeTab === "links" && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
              <div className="border-l-4 border-purple-500 pl-4 mb-8">
                <h3 className="text-lg font-bold text-slate-800">Links & Referências</h3>
                <p className="text-sm text-slate-500">Construindo autoridade e link building interno.</p>
              </div>
              <div className="grid grid-cols-1 gap-6">
                {renderField("Artigos Relacionados Internos", "artigos_relacionados_internos", "textarea")}
                {renderField("Anchors Internas Sugeridas", "anchors_internas_sugeridas", "textarea")}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {renderField("Cluster Temática", "cluster_tematica")}
                  {renderField("Artigo Pilar (Cornerstone)?", "artigo_pilar", "select", "", ["Sim", "Não"])}
                </div>
                {renderField("Links Externos de Autoridade", "links_externos_autoridade", "textarea")}
                {renderField("Referências Obrigatórias", "referencias_obrigatorias", "textarea")}
                {renderField("Referências Complementares", "referencias_complementares", "textarea")}
              </div>
            </div>
          )}

          {activeTab === "imagem" && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
              <div className="border-l-4 border-pink-500 pl-4 mb-8">
                <h3 className="text-lg font-bold text-slate-800">Imagem de Capa</h3>
                <p className="text-sm text-slate-500">Direcionais visuais para geração ou escolha da capa.</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {renderField("Ideia da Imagem", "ideia_imagem_capa", "textarea")}
                {renderField("Prompt para IA (DALL-E/Midjourney)", "prompt_imagem_capa", "textarea")}
                {renderField("Texto na Imagem (se houver)", "texto_na_imagem")}
                {renderField("Estilo Visual", "estilo_visual_capa", "select", "", ["Minimalista", "Fotorealista", "Ilustração 3D", "Infográfico"])}
                {renderField("Paleta Sugerida", "paleta_sugerida")}
                {renderField("Elementos Obrigatórios", "elementos_visuais_obrigatorios")}
                {renderField("Elementos Proibidos", "elementos_visuais_proibidos")}
                {renderField("Proporção", "proporcao_imagem", "select", "", ["16:9", "4:3", "1:1"])}
                {renderField("Alt Text (SEO)", "alt_text")}
                {renderField("Legenda", "legenda_imagem")}
              </div>
            </div>
          )}

          {activeTab === "publicacao" && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
              <div className="border-l-4 border-slate-800 pl-4 mb-8">
                <h3 className="text-lg font-bold text-slate-800">Publicação & Admin</h3>
                <p className="text-sm text-slate-500">Configurações para o destino final no WordPress.</p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {renderField("Categoria WordPress", "categoria_wordpress")}
                {renderField("Tags WordPress", "tags_wordpress", "text", "Separadas por vírgula")}
                {renderField("Autor Sugerido", "autor")}
                {renderField("Data Planejada", "data_planejada", "date")}
                <div className="col-span-1 md:col-span-2">
                  {renderField("Observações Editoriais (Uso Interno)", "observacoes_editoriais", "textarea")}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </form>
  );
}
