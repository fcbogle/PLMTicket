from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import re
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.database import SessionLocal
from backend.app.services.imports import merge_csv


def infer_sort_key(path: Path) -> tuple[datetime, str]:
    name = path.name

    yyyymmdd_match = re.search(r"(\d{8})", name)
    if yyyymmdd_match:
        return datetime.strptime(yyyymmdd_match.group(1), "%Y%m%d"), name

    ddmmyyyy_match = re.search(r"(\d{2})-(\d{2})-(\d{4})", name)
    if ddmmyyyy_match:
        day, month, year = ddmmyyyy_match.groups()
        return datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d"), name

    return datetime.fromtimestamp(path.stat().st_mtime), name


def main() -> None:
    parser = argparse.ArgumentParser(description="Reimport every vendor CSV in a folder into the local PLM ticket database.")
    parser.add_argument("folder_path", help="Folder containing vendor CSV files")
    args = parser.parse_args()

    folder = Path(args.folder_path).expanduser().resolve()
    if not folder.exists() or not folder.is_dir():
        raise SystemExit(f"Folder not found: {folder}")

    csv_files = sorted(folder.glob("*.csv"), key=infer_sort_key)
    if not csv_files:
        raise SystemExit(f"No CSV files found in: {folder}")

    db = SessionLocal()
    try:
        for path in csv_files:
            result = merge_csv(db, path.read_bytes())
            print(path.name, result.model_dump())
    finally:
        db.close()


if __name__ == "__main__":
    main()
