import argparse
import sys
from pathlib import Path

from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test local do fluxo editorial.")
    parser.add_argument(
        "--include-wordpress",
        action="store_true",
        help="Inclui o diagnostico read-only da conexao WordPress.",
    )
    args = parser.parse_args()

    endpoints = ["/health", "/api/v1/editorial/pautas"]
    if args.include_wordpress:
        endpoints.append("/api/v1/editorial/system/status")

    client = TestClient(app)
    failed = False
    for endpoint in endpoints:
        response = client.get(endpoint)
        status = "OK" if response.status_code == 200 else "FALHOU"
        print(f"{status}: GET {endpoint} -> {response.status_code}")
        if response.status_code != 200:
            failed = True
            print(response.text[:500])
        elif endpoint.endswith("/system/status"):
            payload = response.json()
            wordpress_status = "conectado" if payload.get("wordpress_connection_ok") else "indisponivel"
            cron_status = "habilitado" if payload.get("cron_enabled") else "desligado"
            print(
                "INFO: WordPress "
                f"{wordpress_status}; cron {cron_status} "
                f"(modo={payload.get('cron_mode')}, dry_run={payload.get('cron_dry_run')})."
            )

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
