from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.repositories.pauta_repository import pauta_repo
from app.schemas.pauta import PautaResponse, PautaUpdate, PautaCreate
from app.utils.excel_parser import parse_excel_pautas
from app.models.pauta import PautaStatus
import pandas as pd
from io import BytesIO
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/", response_model=List[PautaResponse])
def read_pautas(
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None,
    area: Optional[str] = None,
    prioridade: Optional[str] = None,
    query: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Listar pautas com filtros avançados e busca"""
    return pauta_repo.search_advanced(
        db, 
        query=query, 
        status=status, 
        area=area, 
        prioridade=prioridade, 
        skip=skip, 
        limit=limit
    )

@router.post("/", response_model=PautaResponse)
def create_pauta(pauta_in: PautaCreate, db: Session = Depends(get_db)):
    """Criar uma nova pauta manualmente"""
    return pauta_repo.create(db, obj_in=pauta_in)

@router.get("/{pauta_id}", response_model=PautaResponse)
def read_pauta(pauta_id: int, db: Session = Depends(get_db)):
    """Detalhar uma pauta"""
    pauta = pauta_repo.get(db, id=pauta_id)
    if not pauta:
        raise HTTPException(status_code=404, detail="Pauta não encontrada")
    return pauta

@router.put("/{pauta_id}", response_model=PautaResponse)
def update_pauta(pauta_id: int, pauta_in: PautaUpdate, db: Session = Depends(get_db)):
    """Atualizar dados da pauta"""
    pauta = pauta_repo.get(db, id=pauta_id)
    if not pauta:
        raise HTTPException(status_code=404, detail="Pauta não encontrada")
    return pauta_repo.update(db, db_obj=pauta, obj_in=pauta_in)

@router.delete("/{pauta_id}")
def delete_pauta(pauta_id: int, db: Session = Depends(get_db)):
    """Excluir uma pauta"""
    pauta = pauta_repo.get(db, id=pauta_id)
    if not pauta:
        raise HTTPException(status_code=404, detail="Pauta não encontrada")
    pauta_repo.remove(db, id=pauta_id)
    return {"message": "Pauta excluída com sucesso"}

@router.post("/{pauta_id}/duplicate", response_model=PautaResponse)
def duplicate_pauta(pauta_id: int, db: Session = Depends(get_db)):
    """Duplicar uma pauta existente"""
    new_pauta = pauta_repo.duplicate(db, id=pauta_id)
    if not new_pauta:
        raise HTTPException(status_code=404, detail="Pauta original não encontrada")
    return new_pauta

@router.post("/{pauta_id}/archive", response_model=PautaResponse)
def archive_pauta(pauta_id: int, db: Session = Depends(get_db)):
    """Arquivar uma pauta"""
    pauta = pauta_repo.get(db, id=pauta_id)
    if not pauta:
        raise HTTPException(status_code=404, detail="Pauta não encontrada")
    return pauta_repo.update(db, db_obj=pauta, obj_in={"status": PautaStatus.ARQUIVADA})

@router.get("/export/excel")
def export_pautas(db: Session = Depends(get_db)):
    """Exportar todas as pautas para Excel"""
    pautas = pauta_repo.get_multi(db, limit=1000)
    
    # Converter para lista de dicionários
    data = []
    for p in pautas:
        p_dict = {c.name: getattr(p, c.name) for c in p.__table__.columns}
        data.append(p_dict)
    
    df = pd.DataFrame(data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Pautas')
    
    output.seek(0)
    
    headers = {
        'Content-Disposition': 'attachment; filename="pautas_export.xlsx"'
    }
    return StreamingResponse(output, headers=headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@router.post("/import")
async def import_pautas(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload de planilha Excel (.xlsx) para importar pautas (Legado/Complementar)"""
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Apenas arquivos .xlsx são suportados.")

    contents = await file.read()
    try:
        valid_pautas, errors = parse_excel_pautas(contents)
        
        # Salvar pautas válidas no banco
        created_count = 0
        for pauta_in in valid_pautas:
            # Garantir que campos vazios sejam bem tratados
            pauta_repo.create(db, obj_in=pauta_in)
            created_count += 1

        return {
            "message": f"{created_count} pautas importadas com sucesso.",
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
