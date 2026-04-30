import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from app.core.config import settings
from app.schemas.editorial import SHEET_COLUMNS, SheetPauta


class ExcelEditorialService:
    def __init__(self) -> None:
        self.path = Path(settings.EXCEL_PAUTAS_PATH)
        self.sheet_name = settings.EXCEL_PAUTAS_SHEET_NAME
        self.backup_dir = Path(settings.EXCEL_BACKUPS_DIR)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _snapshot_workbook(self) -> None:
        if not self.path.exists():
            return
        backup_path = self.backup_dir / f"{self.path.stem}_{self._timestamp()}{self.path.suffix}"
        shutil.copy2(self.path, backup_path)

    def ensure_workbook(self) -> None:
        if self.path.exists():
            try:
                df = pd.read_excel(self.path, sheet_name=self.sheet_name, dtype=str).fillna("")
                if list(df.columns) == SHEET_COLUMNS:
                    return
            except Exception:
                pass
        df = pd.DataFrame(columns=SHEET_COLUMNS)
        with pd.ExcelWriter(self.path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=self.sheet_name, index=False)

    def _read_df(self) -> pd.DataFrame:
        self.ensure_workbook()
        return pd.read_excel(self.path, sheet_name=self.sheet_name, dtype=str).fillna("")

    def _write_df(self, df: pd.DataFrame) -> None:
        ordered = df.reindex(columns=SHEET_COLUMNS, fill_value="")
        with pd.ExcelWriter(self.path, engine="openpyxl") as writer:
            ordered.to_excel(writer, sheet_name=self.sheet_name, index=False)
        self._snapshot_workbook()

    def list_pautas(self) -> List[SheetPauta]:
        df = self._read_df()
        pautas = []
        for _, row in df.iterrows():
            data = {column: str(row.get(column, "") or "") for column in SHEET_COLUMNS}
            if data["ID"].strip():
                pautas.append(SheetPauta(**data))
        return pautas

    def append_pautas(self, pautas: List[SheetPauta]) -> None:
        if not pautas:
            return
        df = self._read_df()
        rows = pd.DataFrame([pauta.model_dump(by_alias=True) for pauta in pautas])
        df = pd.concat([df, rows], ignore_index=True)
        self._write_df(df)

    def next_id(self) -> int:
        ids = []
        for pauta in self.list_pautas():
            try:
                ids.append(int(str(pauta.id)))
            except ValueError:
                continue
        return max(ids) + 1 if ids else 1

    def get_pauta_by_id(self, pauta_id: str) -> Optional[SheetPauta]:
        for pauta in self.list_pautas():
            if str(pauta.id) == str(pauta_id):
                return pauta
        return None

    def update_row(self, pauta_id: str, updates: Dict[str, str]) -> Optional[SheetPauta]:
        df = self._read_df()
        mask = df["ID"].astype(str) == str(pauta_id)
        if not mask.any():
            return None
        for column, value in updates.items():
            if column in df.columns:
                df.loc[mask, column] = value
        self._write_df(df)
        row = df[mask].iloc[0].to_dict()
        normalized = {column: str(row.get(column, "") or "") for column in SHEET_COLUMNS}
        return SheetPauta(**normalized)

    def seed_initial_pautas(self) -> List[SheetPauta]:
        existing = self.list_pautas()
        if existing:
            return existing

        created_at = datetime.now().strftime("%Y-%m-%d")
        pautas = [
            SheetPauta(
                **{
                    "ID": "1",
                    "Status": "Pendente",
                    "Prioridade": "Alta",
                    "Tema": "Como usar active recall na medicina sem esquecer o conteúdo",
                    "Titulo sugerido": "Como usar active recall na medicina (sem esquecer tudo)",
                    "Categoria": "Aprendizagem",
                    "Palavra-chave principal": "active recall medicina",
                    "Palavras-chave secundarias": "como estudar medicina, revisao ativa, memorizacao medicina",
                    "Volume de busca": "2400",
                    "Dificuldade SEO": "Media",
                    "Intencao de busca": "Informacional",
                    "Posicao no funil": "Topo",
                    "CTA sugerido": "Conheça o EasyCards",
                    "Produto sugerido": "EasyCards",
                    "Tamanho recomendado": "2000 palavras",
                    "Topicos obrigatorios": "o que e active recall, como aplicar na medicina, erros comuns, exemplo pratico",
                    "Topicos proibidos": "motivacao generica, teoria sem aplicacao",
                    "Observacoes editoriais": "Tom direto e pratico; abrir confrontando o erro do estudante.",
                    "SEO rationale": "Keyword central do nicho e altamente alinhada ao produto principal.",
                    "Data criacao": created_at,
                }
            ),
            SheetPauta(
                **{
                    "ID": "2",
                    "Status": "Pendente",
                    "Prioridade": "Alta",
                    "Tema": "Como criar flashcards realmente bons no Anki para medicina",
                    "Titulo sugerido": "Como criar flashcards no Anki que funcionam na medicina",
                    "Categoria": "Ferramentas",
                    "Palavra-chave principal": "como criar flashcards no anki",
                    "Palavras-chave secundarias": "anki medicina, flashcards medicina, erros no anki",
                    "Volume de busca": "1900",
                    "Dificuldade SEO": "Facil",
                    "Intencao de busca": "Informacional",
                    "Posicao no funil": "Meio",
                    "CTA sugerido": "Conheça o EasyCards",
                    "Produto sugerido": "EasyCards",
                    "Tamanho recomendado": "2200 palavras",
                    "Topicos obrigatorios": "o que faz um flashcard ruim, regra de simplicidade, exemplos bons e ruins, revisao",
                    "Topicos proibidos": "listas vazias de dicas, comparacoes superficiais",
                    "Observacoes editoriais": "Enfatizar erro operacional e mostrar correcao passo a passo.",
                    "SEO rationale": "Boa oportunidade para keyword transacional leve com forte ponte para EasyCards.",
                    "Data criacao": created_at,
                }
            ),
            SheetPauta(
                **{
                    "ID": "3",
                    "Status": "Pendente",
                    "Prioridade": "Alta",
                    "Tema": "Como estudar para residencia medica com metodo e revisao",
                    "Titulo sugerido": "Como estudar para residencia medica sem desperdiçar tempo",
                    "Categoria": "Medicina",
                    "Palavra-chave principal": "como estudar para residencia medica",
                    "Palavras-chave secundarias": "cronograma residencia, revisao residencia, estrategia de estudo",
                    "Volume de busca": "3600",
                    "Dificuldade SEO": "Media",
                    "Intencao de busca": "Informacional",
                    "Posicao no funil": "Fundo",
                    "CTA sugerido": "Acesse o EMR",
                    "Produto sugerido": "EMR",
                    "Tamanho recomendado": "2500 palavras",
                    "Topicos obrigatorios": "erro de estudar sem estrategia, organizacao semanal, revisao, questoes, acompanhamento",
                    "Topicos proibidos": "promessas milagrosas, motivacao vazia",
                    "Observacoes editoriais": "Direto, autoridade de performance, foco em aprovacao.",
                    "SEO rationale": "Keyword principal do funil de conversao para residencia.",
                    "Data criacao": created_at,
                }
            ),
            SheetPauta(
                **{
                    "ID": "4",
                    "Status": "Pendente",
                    "Prioridade": "Alta",
                    "Tema": "Como revisar medicina sem esquecer o que foi estudado",
                    "Titulo sugerido": "Como revisar medicina sem esquecer tudo depois",
                    "Categoria": "Aprendizagem",
                    "Palavra-chave principal": "como revisar medicina",
                    "Palavras-chave secundarias": "repeticao espacada medicina, revisao medicina, memoria de longo prazo",
                    "Volume de busca": "1300",
                    "Dificuldade SEO": "Media",
                    "Intencao de busca": "Informacional",
                    "Posicao no funil": "Meio",
                    "CTA sugerido": "Conheça o EasyCards",
                    "Produto sugerido": "EasyCards",
                    "Tamanho recomendado": "1800 palavras",
                    "Topicos obrigatorios": "por que esquecer e normal, janela de revisao, sistema de repeticao, exemplos praticos",
                    "Topicos proibidos": "conteudo clinico puro",
                    "Observacoes editoriais": "Explicar a dor e entregar um sistema repetivel.",
                    "SEO rationale": "Termo de dor forte e ponte direta para repeticao espacada e flashcards.",
                    "Data criacao": created_at,
                }
            ),
        ]
        self.append_pautas(pautas)
        return self.list_pautas()


excel_editorial_service = ExcelEditorialService()
