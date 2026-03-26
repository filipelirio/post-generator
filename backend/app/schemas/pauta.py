from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, Any
from datetime import datetime
from app.models.pauta import PautaStatus

class PautaBase(BaseModel):
    # Identificação & Classificação
    prioridade: Optional[str] = None
    area: Optional[str] = None
    subarea: Optional[str] = None
    categoria_principal: Optional[str] = None
    tema: str
    titulo_base: Optional[str] = None
    
    # SEO & Estratégia
    palavra_chave_principal: Optional[str] = ""
    palavras_chave_secundarias: Optional[str] = None
    intencao_de_busca: Optional[str] = None
    publico_alvo: Optional[str] = None
    objetivo_do_artigo: Optional[str] = None
    estagio_do_funil: Optional[str] = None
    angulo_seo: Optional[str] = None
    pergunta_principal_do_usuario: Optional[str] = None
    
    # Estrutura do Conteúdo
    resumo_da_pauta: Optional[str] = None
    outline_h2_h3: Optional[str] = None
    topicos_obrigatorios: Optional[str] = None
    topicos_proibidos: Optional[str] = None
    tom_de_voz: Optional[str] = None
    nivel_de_profundidade: Optional[str] = None
    formato_do_artigo: Optional[str] = None
    tamanho_estimado: Optional[str] = None
    perguntas_frequentes_desejadas: Optional[str] = None
    restricoes_editoriais: Optional[str] = None
    
    # Monetização & CTA
    objetivo_de_conversao: Optional[str] = None
    produto_relacionado: Optional[str] = None
    servico_relacionado: Optional[str] = None
    cta_principal: Optional[str] = None
    cta_secundario: Optional[str] = None
    bloco_promocional_1: Optional[str] = None
    bloco_promocional_2: Optional[str] = None
    link_de_destino_cta: Optional[str] = None
    momento_do_anuncio: Optional[str] = None
    tipo_de_anuncio: Optional[str] = None
    
    # Links & Referências
    artigos_relacionados_internos: Optional[str] = None
    anchors_internas_sugeridas: Optional[str] = None
    cluster_tematica: Optional[str] = None
    artigo_pilar: Optional[str] = None
    links_externos_autoridade: Optional[str] = None
    referencias_obrigatorias: Optional[str] = None
    referencias_complementares: Optional[str] = None
    
    # Imagem de Capa
    ideia_imagem_capa: Optional[str] = None
    prompt_imagem_capa: Optional[str] = None
    texto_na_imagem: Optional[str] = None
    estilo_visual_capa: Optional[str] = None
    paleta_sugerida: Optional[str] = None
    elementos_visuais_obrigatorios: Optional[str] = None
    elementos_visuais_proibidos: Optional[str] = None
    proporcao_imagem: Optional[str] = None
    alt_text: Optional[str] = None
    legenda_imagem: Optional[str] = None
    
    # Publicação & Admin
    categoria_wordpress: Optional[str] = None
    tags_wordpress: Optional[str] = None
    autor: Optional[str] = None
    @field_validator("*", mode="before")
    @classmethod
    def empty_string_to_none(cls, v: Any) -> Any:
        if v == "":
            return None
        return v

    data_planejada: Optional[datetime] = None
    observacoes_editoriais: Optional[str] = None

class PautaCreate(PautaBase):
    pass

class PautaUpdate(PautaBase):
    tema: Optional[str] = None # No update o tema pode ser opcional
    status: Optional[PautaStatus] = None
    error_message: Optional[str] = None

class PautaResponse(PautaBase):
    id: int
    status: PautaStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
