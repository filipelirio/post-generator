import threading
from typing import Iterable

from app.schemas.editorial import AutomationAction, AutomationRunRequest, AutomationRunResponse, SheetPauta
from app.services.editorial_article_service import editorial_article_service
from app.services.editorial_publish_service import editorial_publish_service
from app.services.excel_editorial_service import excel_editorial_service


class EditorialCronService:
    def __init__(
        self,
        excel_service=excel_editorial_service,
        article_service=editorial_article_service,
        publish_service=editorial_publish_service,
    ) -> None:
        self.excel_service = excel_service
        self.article_service = article_service
        self.publish_service = publish_service
        self._run_lock = threading.Lock()

    def _prioritized(self, pautas: Iterable[SheetPauta], statuses: list[str]) -> list[SheetPauta]:
        status_order = {status: index for index, status in enumerate(statuses)}
        candidates = [pauta for pauta in pautas if pauta.status in status_order]
        return sorted(
            candidates,
            key=lambda pauta: (
                status_order[pauta.status],
                0 if pauta.prioridade.strip().lower() == "alta" else 1,
                (0, int(pauta.id)) if pauta.id.isdigit() else (1, pauta.id),
            ),
        )

    def _select_candidates(self, request: AutomationRunRequest) -> list[SheetPauta]:
        pautas = self.excel_service.list_pautas()
        if request.mode == "generate_only":
            candidates = self._prioritized(pautas, ["Pendente"])
        elif request.mode == "draft":
            candidates = self._prioritized(pautas, ["Em producao", "Pendente"])
        elif request.allow_unreviewed_publish:
            candidates = self._prioritized(pautas, ["Rascunho", "Em producao", "Pendente"])
        else:
            # Live publication is limited to articles already staged in WordPress as drafts.
            candidates = self._prioritized(pautas, ["Rascunho"])
        return candidates[: request.max_items]

    def _describe_dry_run(self, pauta: SheetPauta, request: AutomationRunRequest) -> AutomationAction:
        if request.mode == "generate_only":
            action = "would_generate_article"
            resulting_status = "Em producao"
        elif request.mode == "draft":
            action = "would_create_wordpress_draft"
            resulting_status = "Rascunho"
        else:
            action = "would_publish_wordpress_post"
            resulting_status = "Publicado"
        return AutomationAction(
            pauta_id=pauta.id,
            previous_status=pauta.status,
            action=action,
            resulting_status=resulting_status,
            details="Simulacao: nenhuma alteracao foi executada.",
        )

    def _execute(self, pauta: SheetPauta, request: AutomationRunRequest) -> AutomationAction:
        previous_status = pauta.status
        if request.mode == "generate_only":
            self.article_service.generate(pauta.id)
            return AutomationAction(
                pauta_id=pauta.id,
                previous_status=previous_status,
                action="generated_article",
                resulting_status="Em producao",
            )

        if previous_status == "Pendente":
            self.article_service.generate(pauta.id)

        publish_status = "publish" if request.mode == "publish" else "draft"
        result = self.publish_service.publish(pauta_id=pauta.id, publish_status=publish_status)
        warnings = result.get("warnings", [])
        details = result.get("message", "")
        if warnings:
            details = f"{details} Avisos: {' | '.join(warnings)}"
        return AutomationAction(
            pauta_id=pauta.id,
            previous_status=previous_status,
            action="published_wordpress_post" if publish_status == "publish" else "created_wordpress_draft",
            resulting_status="Publicado" if publish_status == "publish" else "Rascunho",
            details=details,
        )

    def run(self, request: AutomationRunRequest) -> AutomationRunResponse:
        if not self._run_lock.acquire(blocking=False):
            raise RuntimeError("Ja existe uma automacao editorial em execucao neste backend.")

        actions: list[AutomationAction] = []
        errors: list[str] = []
        try:
            candidates = self._select_candidates(request)
            for pauta in candidates:
                try:
                    action = self._describe_dry_run(pauta, request) if request.dry_run else self._execute(pauta, request)
                    actions.append(action)
                except Exception as exc:
                    errors.append(f"Pauta {pauta.id}: {exc}")
                    break
            return AutomationRunResponse(
                mode=request.mode,
                dry_run=request.dry_run,
                processed_count=len(actions),
                actions=actions,
                errors=errors,
            )
        finally:
            self._run_lock.release()


editorial_cron_service = EditorialCronService()
