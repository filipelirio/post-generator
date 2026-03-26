from pydantic import BaseModel, ConfigDict
from typing import Optional, List

# ---- PLANNER ----
class PlannerResponse(BaseModel):
    editorial_strategy: str
    seo_title: str
    human_title: str
    slug: str
    meta_title: str
    meta_description: str
    excerpt: str
    outline: str

    model_config = ConfigDict(extra="ignore")

# ---- WRITER ----
class FAQItem(BaseModel):
    question: str
    answer: str

class WriterResponse(BaseModel):
    article_html: str
    faq_json: List[FAQItem]
    cta: str
    internal_link_suggestions: Optional[str] = None
    external_link_suggestions: Optional[str] = None
    cover_image_prompt: str
    cover_image_alt: str

    model_config = ConfigDict(extra="ignore")

# ---- REVISION ----
class RevisionResponse(BaseModel):
    revised_article_html: str
    revised_meta_description: str
    revised_excerpt: str
    quality_notes: str
    seo_notes: str

    model_config = ConfigDict(extra="ignore")
