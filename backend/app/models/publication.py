from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class PublicationRecord(Base):
    __tablename__ = "publication_record"

    id = Column(Integer, primary_key=True, index=True)
    pauta_id = Column(Integer, ForeignKey("pauta.id"), nullable=False)
    
    # Retorno do WordPress
    wordpress_post_id = Column(Integer, nullable=True, index=True)
    wordpress_url = Column(String(500), nullable=True)
    wordpress_media_id = Column(Integer, nullable=True) # ID da imagem destacada no WP
    
    status = Column(String(20), nullable=False, default="draft") # draft ou publish
    published_at = Column(DateTime, default=datetime.utcnow)
    
    # Resposta bruta para log/auditoria
    raw_response_json = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    pauta = relationship("Pauta", back_populates="publications")
