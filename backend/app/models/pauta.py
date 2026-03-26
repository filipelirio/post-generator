from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base
import enum

class PautaStatus(str, enum.Enum):
    PENDENTE = "pendente"
    IMPORTADA = "importada"
    GERADA = "gerada"
    REVISADA = "revisada"
    PRONTA = "pronta"
    PUBLICADA = "publicada"
    ERRO = "erro"
    ARQUIVADA = "arquivada"

class Pauta(Base):
    __tablename__ = "pauta"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Identificação & Classificação
    prioridade = Column(String(50), nullable=True) # Alta, Média, Baixa
    area = Column(String(100), nullable=True)
    subarea = Column(String(100), nullable=True)
    categoria_principal = Column(String(100), nullable=True)
    tema = Column(String(255), nullable=False, index=True)
    titulo_base = Column(String(255), nullable=True)
    
    # SEO & Estratégia
    palavra_chave_principal = Column(String(255), nullable=True, index=True)
    palavras_chave_secundarias = Column(Text, nullable=True)
    intencao_de_busca = Column(String(255), nullable=True)
    publico_alvo = Column(String(255), nullable=True)
    objetivo_do_artigo = Column(Text, nullable=True)
    estagio_do_funil = Column(String(100), nullable=True)
    angulo_seo = Column(String(255), nullable=True)
    pergunta_principal_do_usuario = Column(Text, nullable=True)
    
    # Estrutura do Conteúdo
    resumo_da_pauta = Column(Text, nullable=True)
    outline_h2_h3 = Column(Text, nullable=True)
    topicos_obrigatorios = Column(Text, nullable=True)
    topicos_proibidos = Column(Text, nullable=True)
    tom_de_voz = Column(String(100), nullable=True)
    nivel_de_profundidade = Column(String(100), nullable=True)
    formato_do_artigo = Column(String(100), nullable=True)
    tamanho_estimado = Column(String(50), nullable=True)
    perguntas_frequentes_desejadas = Column(Text, nullable=True)
    restricoes_editoriais = Column(Text, nullable=True)
    
    # Monetização & CTA
    objetivo_de_conversao = Column(Text, nullable=True)
    produto_relacionado = Column(String(255), nullable=True)
    servico_relacionado = Column(String(255), nullable=True)
    cta_principal = Column(Text, nullable=True)
    cta_secundario = Column(Text, nullable=True)
    bloco_promocional_1 = Column(Text, nullable=True)
    bloco_promocional_2 = Column(Text, nullable=True)
    link_de_destino_cta = Column(String(255), nullable=True)
    momento_do_anuncio = Column(String(100), nullable=True)
    tipo_de_anuncio = Column(String(100), nullable=True)
    
    # Links & Referências
    artigos_relacionados_internos = Column(Text, nullable=True)
    anchors_internas_sugeridas = Column(Text, nullable=True)
    cluster_tematica = Column(String(255), nullable=True)
    artigo_pilar = Column(String(255), nullable=True)
    links_externos_autoridade = Column(Text, nullable=True)
    referencias_obrigatorias = Column(Text, nullable=True)
    referencias_complementares = Column(Text, nullable=True)
    
    # Imagem de Capa
    ideia_imagem_capa = Column(Text, nullable=True)
    prompt_imagem_capa = Column(Text, nullable=True)
    texto_na_imagem = Column(String(255), nullable=True)
    estilo_visual_capa = Column(String(255), nullable=True)
    paleta_sugerida = Column(String(255), nullable=True)
    elementos_visuais_obrigatorios = Column(Text, nullable=True)
    elementos_visuais_proibidos = Column(Text, nullable=True)
    proporcao_imagem = Column(String(50), nullable=True)
    alt_text = Column(String(255), nullable=True)
    legenda_imagem = Column(Text, nullable=True)
    
    # Publicação & Admin
    categoria_wordpress = Column(String(255), nullable=True)
    tags_wordpress = Column(String(255), nullable=True)
    autor = Column(String(100), nullable=True)
    data_planejada = Column(DateTime, nullable=True)
    observacoes_editoriais = Column(Text, nullable=True)
    
    # Controle
    status = Column(String(20), default=PautaStatus.PENDENTE, nullable=False)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    drafts = relationship("ArticleDraft", back_populates="pauta", cascade="all, delete-orphan")
    publications = relationship("PublicationRecord", back_populates="pauta", cascade="all, delete-orphan")
