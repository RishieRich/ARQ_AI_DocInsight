# -----------------------------------------------------------------------------
# AI Doc Agent - command-line entry point for the ingestion workflow.
# -----------------------------------------------------------------------------
"""AI Doc Agent CLI entry point.

This module wires together the ingestion helpers, configures run-scoped logging,
and exposes a simple ``main`` runner that can be invoked via ``python main.py``.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

from src.agents.ingestion_agent import ingest_file_from_path, list_input_files
from src.core.logging_utils import configure_run_logger


def run_ingestion(input_dir: Path) -> List[Dict[str, object]]:
    """Run the ingestion sequence for every supported file in ``input_dir``."""
    logging.info("Starting ingestion run for directory: %s", input_dir)
    ingested_results: List[Dict[str, object]] = []

    # Ask the ingestion agent for all supported files prior to iterating.
    files = list_input_files(input_dir)
    if not files:
        logging.warning("No eligible files found in %s", input_dir)
        return ingested_results

    # Process each file sequentially so log output stays easy to read.
    for file_path in files:
        logging.info("Ingesting %s", file_path)
        ingested_results.append(ingest_file_from_path(file_path))

    logging.info("Completed ingestion run. %d file(s) processed.", len(ingested_results))
    return ingested_results


def main() -> None:
    project_root = Path(__file__).resolve().parent
    input_dir = project_root / "input"
    log_file = configure_run_logger(app_name="cli_ingestion")
    logging.info("CLI logging initialised. Run log file: %s", log_file)

    try:
        ingested_files = run_ingestion(input_dir)
    except (FileNotFoundError, NotADirectoryError) as exc:
        logging.error("Ingestion failed: %s", exc)
        return

    # Mirror ingestion summaries after the run completes.
    for file_info in ingested_files:
        logging.info(
            "Ingested file '%s' (%s) with id=%s size=%d bytes",
            file_info["name"],
            file_info["extension"],
            file_info["file_id"],
            file_info["size_bytes"],
        )


if __name__ == "__main__":
    main()
