from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class ArticleDraftBase(BaseModel):
    editorial_strategy: Optional[str] = None
    seo_title: Optional[str] = None
    human_title: Optional[str] = None
    slug: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    excerpt: Optional[str] = None
    outline: Optional[str] = None
    
    article_html: Optional[str] = None
    faq_json: Optional[str] = None
    cta: Optional[str] = None
    
    internal_link_suggestions: Optional[str] = None
    external_link_suggestions: Optional[str] = None
    
    cover_image_prompt: Optional[str] = None
    cover_image_alt: Optional[str] = None
    cover_image_url: Optional[str] = None

class ArticleDraftCreate(ArticleDraftBase):
    pauta_id: int

class ArticleDraftUpdate(ArticleDraftBase):
    pass

class ArticleDraftResponse(ArticleDraftBase):
    id: int
    pauta_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ArticleVersionResponse(BaseModel):
    id: int
    draft_id: int
    version_number: int
    article_html: Optional[str] = None
    meta_description: Optional[str] = None
    faq_json: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
