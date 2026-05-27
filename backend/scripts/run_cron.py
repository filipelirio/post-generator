import argparse
import json
import sys
from pathlib import Path

import requests

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Executa um ciclo da automacao editorial Easy Artigos.")
    parser.add_argument(
        "--mode",
        choices=["generate_only", "draft", "publish"],
        default=settings.CRON_MODE,
        help="Etapa automatizada. publish so publica rascunhos por padrao.",
    )
    parser.add_argument("--max-items", type=int, default=settings.CRON_MAX_ITEMS, choices=range(1, 6))
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Executa alteracoes. Sem esta flag, o comando apenas simula o ciclo.",
    )
    publication_group = parser.add_mutually_exclusive_group()
    publication_group.add_argument(
        "--allow-unreviewed-publish",
        dest="allow_unreviewed_publish",
        action="store_true",
        default=None,
        help="Permite publicar conteudo ainda nao revisado em modo publish.",
    )
    publication_group.add_argument(
        "--reviewed-only",
        dest="allow_unreviewed_publish",
        action="store_false",
        help="Sobrescreve a configuracao e publica apenas itens ja em rascunho.",
    )
    parser.add_argument(
        "--api-url",
        default=f"http://127.0.0.1:8000{settings.API_V1_STR}/editorial/automation/run",
        help="URL interna do endpoint de automacao do backend em execucao.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not settings.CRON_TOKEN:
        print("CRON_TOKEN nao configurado. A automacao nao pode ser autenticada.", file=sys.stderr)
        return 2

    payload = {
        "mode": args.mode,
        "max_items": args.max_items,
        "dry_run": not args.execute,
        "allow_unreviewed_publish": (
            settings.CRON_ALLOW_UNREVIEWED_PUBLISH
            if args.allow_unreviewed_publish is None
            else args.allow_unreviewed_publish
        ),
    }
    try:
        response = requests.post(
            args.api_url,
            json=payload,
            headers={"X-Cron-Token": settings.CRON_TOKEN},
            timeout=1800,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        detail = ""
        if getattr(exc, "response", None) is not None:
            detail = f" Resposta: {exc.response.text}"
        print(f"Falha ao chamar a automacao: {exc}.{detail}", file=sys.stderr)
        return 1

    result = response.json()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())
