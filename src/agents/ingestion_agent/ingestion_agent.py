# -----------------------------------------------------------------------------
# AI Doc Agent - ingestion helpers shared by CLI and UI entry points.
# -----------------------------------------------------------------------------
"""
Helpers for scanning the local input directory and normalizing raw files for
downstream processing. These functions power the ingestion agent by
discovering the relevant files and turning each file into a consistent,
metadata-rich dictionary.
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Dict, List

# Module-level logger so callers can integrate with their logging setup.
logger = logging.getLogger(__name__)

# Extensions that should be picked up when the caller does not provide a custom list.
DEFAULT_ALLOWED_EXTENSIONS: tuple[str, ...] = ("pdf", "txt", "docx", "csv", "xlsx")


def list_input_files(
    input_dir: Path,
    allowed_extensions: list[str] | None = None,
) -> List[Path]:
    """Return files inside *input_dir* matching the desired extensions."""
    logger.info("Listing input files in directory: %s", input_dir)

    # Validate that the directory exists before doing any additional work.
    if not input_dir.exists():
        logger.error("Input directory %s was not found.", input_dir)
        raise FileNotFoundError(f"Input directory '{input_dir}' was not found.")

    # Ensure that the provided path is actually a directory.
    if not input_dir.is_dir():
        logger.error("Path %s is not a directory.", input_dir)
        raise NotADirectoryError(f"'{input_dir}' is not a directory.")

    # Use the defaults if the caller did not provide an explicit allow list.
    allowed = allowed_extensions if allowed_extensions is not None else list(DEFAULT_ALLOWED_EXTENSIONS)
    logger.debug("Allowed extensions resolved to: %s", allowed)

    # Normalize extensions by stripping leading dots and forcing lowercase for comparisons.
    normalized_exts = {ext.lstrip(".").lower() for ext in allowed}

    matching_files: List[Path] = []
    for file_path in input_dir.iterdir():
        # Skip directories or anything that is not a file.
        if not file_path.is_file():
            logger.debug("Skipping non-file entry: %s", file_path)
            continue

        # Extract and normalize the file's extension.
        ext = file_path.suffix.lstrip(".").lower()
        logger.debug("Evaluating file %s with extension %s", file_path, ext)

        # Keep only files that match one of the allowed extensions.
        if ext in normalized_exts:
            logger.info("Queued file for ingestion: %s", file_path)
            matching_files.append(file_path)
        else:
            logger.debug("Skipping file %s due to unsupported extension.", file_path)

    # Sort for deterministic output, which helps during testing and logging comparisons.
    ordered_files = sorted(matching_files)
    logger.info("Found %d eligible file(s) in %s", len(ordered_files), input_dir)
    return ordered_files


def ingest_file_from_path(path: Path) -> Dict[str, object]:
    """Read a local file path and return a normalized ingestion dictionary."""
    logger.info("Ingesting file at path: %s", path)

    # Confirm the target path exists on disk.
    if not path.exists():
        logger.error("File %s does not exist.", path)
        raise FileNotFoundError(f"File '{path}' does not exist.")

    # Ensure we were given a regular file instead of a directory.
    if not path.is_file():
        logger.error("Path %s is not a file.", path)
        raise IsADirectoryError(f"'{path}' is not a file.")

    # Read the content to memory; downstream processes may turn bytes into chunks.
    content_bytes = path.read_bytes()

    # Compute metadata up front to avoid repeated filesystem calls later.
    extension = path.suffix.lstrip(".").lower()
    file_stat = path.stat()
    logger.debug(
        "File metadata - name: %s, extension: %s, size_bytes: %d",
        path.name,
        extension,
        file_stat.st_size,
    )

    # Compose the ingestion dictionary with a short UUID for traceability.
    ingestion_result = {
        "file_id": f"F-{uuid.uuid4().hex[:8]}",
        "name": path.name,
        "extension": extension,
        "source": "local_folder",
        "path": str(path),
        "size_bytes": file_stat.st_size,
        "content_bytes": content_bytes,
    }
    logger.info("File %s ingested successfully.", path)
    return ingestion_result
