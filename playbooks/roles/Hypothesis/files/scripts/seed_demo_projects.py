#!/usr/bin/env python3
"""Import demo hypothesis projects (e.g. "Sample: Obesity") from MinIO.

Fast subset of seed_database.py - skips the slow GWAS library enrichment.
"""
import os
import sys

sys.path.insert(0, "/app")

from src.db import DemoTemplateHandler
from src.services.storage import create_minio_client_from_env


def main() -> int:
    mongodb_uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("DB_NAME")
    if not mongodb_uri or not db_name:
        print("Missing MONGODB_URI/DB_NAME")
        return 1

    storage = create_minio_client_from_env()
    if storage is None:
        print("MinIO not configured; skipping demo project import.")
        return 1

    handler = DemoTemplateHandler(mongodb_uri, db_name)
    results = handler.ensure_seeds_from_minio(storage)
    print(
        f"Demo projects: imported={results['imported']} "
        f"skipped={results['skipped']} failed={results['failed']}"
    )
    return 1 if results["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
