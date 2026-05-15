from __future__ import annotations

import argparse
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.database import SessionLocal
from backend.app.models import Ticket


def main() -> None:
    parser = argparse.ArgumentParser(description="Show the latest vendor date values from the local PLM ticket database.")
    parser.add_argument("--limit", type=int, default=15, help="Number of rows to display")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        rows = (
            db.query(Ticket.vendor_ticket_id, Ticket.vendor_last_updated, Ticket.vendor_created_date)
            .order_by(Ticket.vendor_last_updated.desc().nullslast(), Ticket.vendor_created_date.desc().nullslast())
            .limit(args.limit)
            .all()
        )
    finally:
        db.close()

    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
