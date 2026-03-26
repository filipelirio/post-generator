from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class ArticleDraft(Base):
    __tablename__ = "article_draft"

    id = Column(Integer, primary_key=True, index=True)
    pauta_id = Column(Integer, ForeignKey("pauta.id"), nullable=False)

    # Metadados e Estratégia (Planner)
    editorial_strategy = Column(Text, nullable=True) # Resumo do planejamento
    seo_title = Column(String(255), nullable=True)
    human_title = Column(String(255), nullable=True)
    slug = Column(String(255), nullable=True)
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(Text, nullable=True)
    excerpt = Column(Text, nullable=True)
    outline = Column(Text, nullable=True) # Estrutura de tópicos

    # Conteúdo (Writer)
    article_html = Column(Text, nullable=True) # Artigo limpo em HTML
    faq_json = Column(Text, nullable=True) # Perguntas e Respostas
    cta = Column(Text, nullable=True) # Botão/Texto de ação final
    
    # Sugestões
    internal_link_suggestions = Column(Text, nullable=True)
    external_link_suggestions = Column(Text, nullable=True)

    # Imagem
    cover_image_prompt = Column(Text, nullable=True)
    cover_image_alt = Column(String(255), nullable=True)
    cover_image_url = Column(String(500), nullable=True) # URL local da imagem gerada

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    pauta = relationship("Pauta", back_populates="drafts")
    versions = relationship("ArticleVersion", back_populates="draft", cascade="all, delete-orphan")

class ArticleVersion(Base):
    __tablename__ = "article_version"

    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(Integer, ForeignKey("article_draft.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    
    # Dados que mudam na versão
    article_html = Column(Text, nullable=True)
    meta_description = Column(Text, nullable=True)
    faq_json = Column(Text, nullable=True)
    
    # Payload da IA para rastreabilidade
    prompt_sent = Column(Text, nullable=True)
    ai_response_raw = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    draft = relationship("ArticleDraft", back_populates="versions")
