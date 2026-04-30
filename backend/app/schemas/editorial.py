from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


SHEET_COLUMNS = [
    "ID",
    "Status",
    "Prioridade",
    "Tema",
    "Titulo sugerido",
    "Categoria",
    "Palavra-chave principal",
    "Palavras-chave secundarias",
    "Volume de busca",
    "Dificuldade SEO",
    "Intencao de busca",
    "Posicao no funil",
    "CTA sugerido",
    "Produto sugerido",
    "Tamanho recomendado",
    "Topicos obrigatorios",
    "Topicos proibidos",
    "Observacoes editoriais",
    "SEO rationale",
    "Data criacao",
    "Data publicacao",
    "URL WordPress",
]


class SheetPauta(BaseModel):
    id: str = Field(alias="ID")
    status: str = Field(default="Pendente", alias="Status")
    prioridade: str = Field(default="Alta", alias="Prioridade")
    tema: str = Field(alias="Tema")
    titulo_sugerido: str = Field(default="", alias="Titulo sugerido")
    categoria: str = Field(default="", alias="Categoria")
    palavra_chave_principal: str = Field(default="", alias="Palavra-chave principal")
    palavras_chave_secundarias: str = Field(default="", alias="Palavras-chave secundarias")
    volume_de_busca: str = Field(default="", alias="Volume de busca")
    dificuldade_seo: str = Field(default="", alias="Dificuldade SEO")
    intencao_de_busca: str = Field(default="", alias="Intencao de busca")
    posicao_no_funil: str = Field(default="", alias="Posicao no funil")
    cta_sugerido: str = Field(default="", alias="CTA sugerido")
    produto_sugerido: str = Field(default="", alias="Produto sugerido")
    tamanho_recomendado: str = Field(default="", alias="Tamanho recomendado")
    topicos_obrigatorios: str = Field(default="", alias="Topicos obrigatorios")
    topicos_proibidos: str = Field(default="", alias="Topicos proibidos")
    observacoes_editoriais: str = Field(default="", alias="Observacoes editoriais")
    seo_rationale: str = Field(default="", alias="SEO rationale")
    data_criacao: str = Field(default="", alias="Data criacao")
    data_publicacao: str = Field(default="", alias="Data publicacao")
    url_wordpress: str = Field(default="", alias="URL WordPress")

    model_config = ConfigDict(populate_by_name=True)

    def to_sheet_row(self) -> List[str]:
        data = self.model_dump(by_alias=True)
        return [str(data.get(column, "") or "") for column in SHEET_COLUMNS]


class GeneratePautasRequest(BaseModel):
    count: int = Field(default=10, ge=1, le=20)
    force_category: Optional[str] = None
    notes: Optional[str] = None


class GeneratePautasResponse(BaseModel):
    created_count: int
    pautas: List[SheetPauta]


class ArticlePackageResponse(BaseModel):
    slug: str
    article_file: str
    seo_file: str
    image_file: str
    preview_html: str
    title: str
    focus_keyword: str


class ArticleDetailResponse(BaseModel):
    slug: str
    pauta_id: str
    title: str
    category: str
    content_html: str
    seo_title: str
    meta_desc: str
    focus_kw: str
    tags: List[str]
    internal_links: List[str]
    external_links: List[str]
    product_mentions: List[str]
    image: dict


class PublishArticleRequest(BaseModel):
    slug: Optional[str] = None
    pauta_id: Optional[str] = None
    publish_status: str = "draft"


class PublishArticleResponse(BaseModel):
    post_id: Optional[int] = None
    url: Optional[str] = None
    status: str
    message: str
    image: Optional[str] = None


class SyncWordPressStatusResponse(BaseModel):
    checked_count: int
    updated_count: int
    message: str


class EditorialSystemStatusResponse(BaseModel):
    openai_configured: bool
    image_generation_enabled: bool
    websearch_enabled: bool
    wordpress_url: str
    wordpress_configured: bool
    wordpress_connection_ok: bool
    excel_path: str
    generated_articles_dir: str
    generated_images_dir: str
    backups_dir: str
