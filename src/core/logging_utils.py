# -----------------------------------------------------------------------------
# AI Doc Agent - centralized logging helpers shared across runtimes.
# -----------------------------------------------------------------------------
"""Logging utilities for consistent, run-scoped log file creation.

Each execution (CLI or Streamlit UI) should invoke ``configure_run_logger`` to
get a run-specific directory and log file that captures everything emitted by
``logging``. This abstraction ensures the directory tree always looks like:

``logs/<YYYYMMDD>/<app>_<YYYYMMDD_HHMMSS>/app_<YYYYMMDD_HHMMSS>.log``
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def _project_root() -> Path:
    """Return the repository root by traversing up from this file."""
    return Path(__file__).resolve().parents[2]


def _build_run_log_paths(app_name: str) -> Tuple[Path, Path]:
    """Return the directory and file path for the current logging run."""
    now = datetime.now()
    date_segment = now.strftime("%Y%m%d")
    run_segment = now.strftime("%Y%m%d_%H%M%S")

    logs_root = _project_root() / "logs"
    run_dir = logs_root / date_segment / f"{app_name}_{run_segment}"
    log_file = run_dir / f"{app_name}_{run_segment}.log"
    return run_dir, log_file


def configure_run_logger(app_name: str, level: int = logging.INFO) -> Path:
    """Configure the root logger to emit console + file logs for this run."""
    run_dir, log_file = _build_run_log_paths(app_name)
    run_dir.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()

    # Reset existing handlers so we do not duplicate output across re-runs.
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        handler.close()

    root_logger.setLevel(level)
    formatter = logging.Formatter(LOG_FORMAT)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    root_logger.info("Logging initialised; writing file logs to %s", log_file)
    return log_file
