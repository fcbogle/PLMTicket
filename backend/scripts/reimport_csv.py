from __future__ import annotations

import argparse
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.database import SessionLocal
from backend.app.services.imports import merge_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Reimport a vendor CSV into the local PLM ticket database.")
    parser.add_argument("csv_path", help="Absolute or relative path to the vendor CSV file")
    args = parser.parse_args()

    path = Path(args.csv_path).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"CSV file not found: {path}")

    contents = path.read_bytes()

    db = SessionLocal()
    try:
        result = merge_csv(db, contents)
    finally:
        db.close()

    print(f"Imported: {path}")
    print(result.model_dump())


if __name__ == "__main__":
    main()
