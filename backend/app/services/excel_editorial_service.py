import shutil
import threading
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
        self._lock = threading.RLock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    def _snapshot_workbook(self) -> None:
        if not self.path.exists():
            return
        backup_path = self.backup_dir / f"{self.path.stem}_{self._timestamp()}{self.path.suffix}"
        shutil.copy2(self.path, backup_path)

    def ensure_workbook(self) -> None:
        with self._lock:
            if self.path.exists():
                try:
                    df = pd.read_excel(self.path, sheet_name=self.sheet_name, dtype=str).fillna("")
                    missing_columns = [column for column in SHEET_COLUMNS if column not in df.columns]
                    if not missing_columns:
                        return
                    for column in missing_columns:
                        df[column] = ""
                    self._write_df(df)
                    return
                except Exception:
                    pass
            df = pd.DataFrame(columns=SHEET_COLUMNS)
            with pd.ExcelWriter(self.path, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name=self.sheet_name, index=False)

    def _read_df(self) -> pd.DataFrame:
        with self._lock:
            self.ensure_workbook()
            return pd.read_excel(self.path, sheet_name=self.sheet_name, dtype=str).fillna("")

    def _write_df(self, df: pd.DataFrame) -> None:
        ordered = df.reindex(columns=SHEET_COLUMNS, fill_value="")
        with self._lock:
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

    def _next_id_from_df(self, df: pd.DataFrame) -> int:
        ids: list[int] = []
        if "ID" not in df.columns:
            return 1
        for value in df["ID"].tolist():
            try:
                ids.append(int(str(value)))
            except ValueError:
                continue
        return max(ids) + 1 if ids else 1

    def append_pautas(self, pautas: List[SheetPauta], assign_new_ids: bool = False) -> List[SheetPauta]:
        if not pautas:
            return []
        with self._lock:
            df = self._read_df()
            if assign_new_ids:
                next_id = self._next_id_from_df(df)
                pautas = [
                    pauta.model_copy(update={"id": str(next_id + index)})
                    for index, pauta in enumerate(pautas)
                ]
            rows = pd.DataFrame([pauta.model_dump(by_alias=True) for pauta in pautas])
            df = pd.concat([df, rows], ignore_index=True)
            self._write_df(df)
            return pautas

    def next_id(self) -> int:
        with self._lock:
            return self._next_id_from_df(self._read_df())

    def get_pauta_by_id(self, pauta_id: str) -> Optional[SheetPauta]:
        for pauta in self.list_pautas():
            if str(pauta.id) == str(pauta_id):
                return pauta
        return None

    def update_row(self, pauta_id: str, updates: Dict[str, str]) -> Optional[SheetPauta]:
        with self._lock:
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


excel_editorial_service = ExcelEditorialService()
