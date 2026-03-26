from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.publication import PublicationRecord
from app.repositories.base import BaseRepository

class PublicationRepository(BaseRepository[PublicationRecord]):
    def __init__(self):
        super().__init__(PublicationRecord)

    def get_by_pauta_id(self, db: Session, pauta_id: int) -> List[PublicationRecord]:
        return db.query(self.model).filter(self.model.pauta_id == pauta_id).all()

    def get_by_wordpress_post_id(self, db: Session, wp_post_id: int) -> Optional[PublicationRecord]:
        return db.query(self.model).filter(self.model.wordpress_post_id == wp_post_id).first()

# Instância global
publication_repo = PublicationRepository()
