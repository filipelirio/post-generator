from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.models.pauta import Pauta, PautaStatus
from app.repositories.base import BaseRepository

class PautaRepository(BaseRepository[Pauta]):
    def __init__(self):
        super().__init__(Pauta)

    def get_by_status(self, db: Session, status: PautaStatus) -> List[Pauta]:
        return db.query(self.model).filter(self.model.status == status).all()

    def search_advanced(
        self, 
        db: Session, 
        *, 
        query: Optional[str] = None, 
        status: Optional[str] = None,
        area: Optional[str] = None,
        prioridade: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Pauta]:
        filters = []
        
        # Filtro de busca textual (tema ou palavra-chave)
        if query:
            filters.append(or_(
                self.model.tema.ilike(f"%{query}%"),
                self.model.palavra_chave_principal.ilike(f"%{query}%")
            ))
            
        # Filtros exatos
        if status:
            filters.append(self.model.status == status)
        if area:
            filters.append(self.model.area == area)
        if prioridade:
            filters.append(self.model.prioridade == prioridade)
            
        return db.query(self.model).filter(*filters).offset(skip).limit(limit).all()

    def duplicate(self, db: Session, *, id: int) -> Optional[Pauta]:
        original = self.get(db, id=id)
        if not original:
            return None
            
        # Criar dicionário excluindo ID e campos automáticos
        data = {c.name: getattr(original, c.name) for c in original.__table__.columns if c.name not in ["id", "created_at", "updated_at"]}
        
        # Ajustes na cópia
        data["tema"] = f"{original.tema} (Cópia)"
        data["status"] = PautaStatus.PENDENTE
        
        return self.create(db, obj_in=data)

# Instância global
pauta_repo = PautaRepository()
