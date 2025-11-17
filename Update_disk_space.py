#!/usr/bin/env python3
"""
update_disk_space.py

Basic utility to record current disk space once per day into a CSV file placed
in the user's profile directory (by default: ~/disk_reports/disk_usage_YYYYMMDD.csv).

- If the daily CSV doesn't exist it will be created with a header.
- Each run appends a timestamped row (so you can run it multiple times per day if desired).
- Uses shutil.disk_usage on the given path (defaults to the user's home directory).

Usage:
    python update_disk_space.py
    # or from another script:
    from update_disk_space import update_daily_disk_csv
    update_daily_disk_csv()
"""
from __future__ import annotations
import os
import shutil
import csv
import datetime
from typing import Optional


def _bytes_to_human(n: int) -> str:
    # Convert bytes to a human readable string (KiB, MiB, ...)
    # Uses 1024 base.
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    value = float(n)
    for unit in units:
        if value < 1024.0:
            return f"{value:.2f} {unit}"
        value /= 1024.0
    return f"{value:.2f} EB"


def update_daily_disk_csv(path_to_check: Optional[str] = None, out_dir: Optional[str] = None) -> str:
    """
    Record the disk usage for `path_to_check` into a CSV named with today's date
    in the user's profile directory (or `out_dir` if provided).

    Args:
        path_to_check: filesystem path to check usage for (default: user's home folder).
        out_dir: output directory to store CSV files (default: ~/disk_reports).

    Returns:
        The full path of the CSV file that was written to.
    """
    home = os.path.expanduser("~")
    if path_to_check is None:
        path_to_check = home
    if out_dir is None:
        out_dir = os.path.join(home, "disk_reports")

    os.makedirs(out_dir, exist_ok=True)

    date_str = datetime.date.today().strftime("%Y%m%d")  # unique date stamp
    filename = f"disk_usage_{date_str}.csv"
    filepath = os.path.join(out_dir, filename)

    # Get disk usage
    usage = shutil.disk_usage(path_to_check)
    total, used, free = usage.total, usage.used, usage.free
    free_pct = (free / total * 100.0) if total else 0.0

    # Row to append
    row = {
        "timestamp": datetime.datetime.now().isoformat(sep=" ", timespec="seconds"),
        "path": path_to_check,
        "total_bytes": str(total),
        "used_bytes": str(used),
        "free_bytes": str(free),
        "free_percent": f"{free_pct:.2f}",
        "total_human": _bytes_to_human(total),
        "used_human": _bytes_to_human(used),
        "free_human": _bytes_to_human(free),
    }

    fieldnames = [
        "timestamp",
        "path",
        "total_bytes",
        "used_bytes",
        "free_bytes",
        "free_percent",
        "total_human",
        "used_human",
        "free_human",
    ]

    write_header = not os.path.exists(filepath)

    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)

    return filepath


if __name__ == "__main__":
    out = update_daily_disk_csv()
    print(f"Wrote disk usage to: {out}")