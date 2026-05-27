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

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
