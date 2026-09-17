"""Run the real API against synthetic cases in an isolated temporary workspace."""

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from backend.demo import load_scenario


def prepare_demo(source: Path, destination: Path) -> None:
    """Copy application code without importing user configuration or datasets."""
    destination.mkdir()  # Refuse to overwrite or merge an existing workspace.
    backend = destination / "backend"
    shutil.copytree(source, backend, ignore=shutil.ignore_patterns(".env", ".env.*", "data", "__pycache__"))
    (backend / "data").mkdir()
    (backend / "data" / "demo.json").write_text(
        json.dumps(load_scenario()["records"], indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    env = os.environ.copy()
    env.update(
        EMBEDDING_PROVIDER="mock",
        LLM_PROVIDER="mock",
        EMBEDDING_DIMENSION="768",
        CLUSTERING_MIN_CLUSTER_SIZE="3",
        CLUSTERING_SIMILARITY_THRESHOLD="0.90",
    )
    # Keep imports inside the copied backend even if a caller set PYTHONPATH.
    env.pop("PYTHONPATH", None)
    with tempfile.TemporaryDirectory(prefix="supportai-demo-") as temporary:
        workspace = Path(temporary) / "app"
        prepare_demo(Path(__file__).resolve().parents[1], workspace)
        print(f"Synthetic receipt demo: 6 cases, mock providers, API port {args.port}", flush=True)
        print("Open the frontend and click Generate / Regenerate FAQs.", flush=True)
        try:
            return subprocess.call(
                [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", str(args.port)],
                cwd=workspace,
                env=env,
            )
        except KeyboardInterrupt:
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
