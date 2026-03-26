from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from app.models.article import ArticleDraft, ArticleVersion
from app.repositories.base import BaseRepository

class ArticleRepository(BaseRepository[ArticleDraft]):
    def __init__(self):
        super().__init__(ArticleDraft)

    def get_by_pauta_id(self, db: Session, pauta_id: int) -> Optional[ArticleDraft]:
        return db.query(self.model).filter(self.model.pauta_id == pauta_id).first()

    def create_version(self, db: Session, *, version_in: dict) -> ArticleVersion:
        db_obj = ArticleVersion(**version_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_versions(self, db: Session, *, draft_id: int) -> List[ArticleVersion]:
        return db.query(ArticleVersion).filter(
            ArticleVersion.draft_id == draft_id
        ).order_by(desc(ArticleVersion.version_number)).all()

# Instância global
article_repo = ArticleRepository()
