"""
Appends a send-result row to log.csv after the payroll email process completes.
"""
from __future__ import annotations

import csv
import os
from datetime import datetime, UTC

import payroll.template_loader as tl

LOG_FILENAME = "log.csv"
_FIELDNAMES = ["timestamp", "email", "name", "sent"]


def _log_path() -> str:
    return str(tl.user_data_dir() / LOG_FILENAME)


def write_log(results: list[dict]) -> str:
    """
    Appends rows to log.csv and returns the file path.

    Each item in `results` must have keys: email, name, sent (bool).
    A UTC timestamp is added automatically.
    """
    path = _log_path()
    file_exists = os.path.isfile(path)
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        for row in results:
            writer.writerow({
                "timestamp": timestamp,
                "email":     row.get("email", ""),
                "name":      row.get("name", ""),
                "sent":      row.get("sent", False),
            })

    return path
