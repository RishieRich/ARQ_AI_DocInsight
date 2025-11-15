# -----------------------------------------------------------------------------
# AI Doc Agent - Streamlit UI for the ingestion workflow.
# -----------------------------------------------------------------------------
"""Streamlit UI for orchestrating AI Doc Agent ingestion runs.

The UI handles uploads, streams results from the ingestion agent, and reports
run-scoped logging locations back to the user for easy debugging.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Dict, List

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.ingestion_agent import (
    DEFAULT_ALLOWED_EXTENSIONS,
    ingest_file_from_path,
    list_input_files,
)
from src.core.logging_utils import configure_run_logger

INPUT_DIR = PROJECT_ROOT / "input"
LOGGER = logging.getLogger(__name__)
LOG_APP_NAME = "streamlit_ui"


def ensure_input_dir() -> Path:
    """Create the input directory if it does not yet exist."""
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOGGER.debug("Ensured input directory exists at %s", INPUT_DIR)
    return INPUT_DIR


def save_uploaded_file(uploaded_file: "st.runtime.uploaded_file_manager.UploadedFile") -> Path:
    """Persist the uploaded file to the input directory."""
    destination = ensure_input_dir() / uploaded_file.name
    destination.write_bytes(uploaded_file.getbuffer())
    LOGGER.info("Persisted uploaded file to %s", destination)
    return destination


def get_existing_files_metadata() -> tuple[List[Dict[str, object]], str | None, bool]:
    """Return current files metadata plus an optional error/info message."""
    try:
        files: List[Path] = list_input_files(INPUT_DIR)
    except FileNotFoundError:
        LOGGER.info("Input directory %s is missing; will prompt the user to upload.", INPUT_DIR)
        return [], "Input folder does not exist yet. Upload a file to create it.", False
    except NotADirectoryError:
        LOGGER.error("Input path %s exists but is not a directory.", INPUT_DIR)
        return [], "Configured input path exists but is not a directory.", True

    metadata = [
        {
            "name": file.name,
            "extension": file.suffix.lstrip("."),
            "size_bytes": file.stat().st_size,
            "path": str(file),
        }
        for file in files
    ]
    return metadata, None, False


def render_existing_files(files_metadata: List[Dict[str, object]], message: str | None, is_error: bool) -> None:
    """Display the files currently queued for ingestion."""
    st.subheader("Files currently in the input folder")

    if message:
        if is_error:
            LOGGER.error("Existing files view error: %s", message)
            st.error(message)
        else:
            LOGGER.info("Existing files view info: %s", message)
            st.info(message)
        return

    if not files_metadata:
        LOGGER.info("Existing files view has no supported assets.")
        st.info("No supported files found in the input folder.")
        return

    st.dataframe(files_metadata, use_container_width=True)


def main() -> None:
    """Entry point for the Streamlit UI runtime."""
    log_path = configure_run_logger(LOG_APP_NAME)
    LOGGER.info("Streamlit UI logging initialised; run log stored at %s", log_path)

    st.set_page_config(page_title="AI Doc Agent", page_icon=":page_facing_up:", layout="centered")
    st.sidebar.success(f"Current run log\n{log_path}")

    st.title("AI Document Ingestion")
    st.write("Upload PDF, TXT, DOCX, CSV, or XLSX files to send them through the ingestion agent.")

    # Separate upload / monitoring experiences via tabs for clarity.
    upload_tab, existing_tab = st.tabs(["Upload & Ingest", "Input Folder Overview"])

    ingestion_details: List[Dict[str, object]] = []  # Stores success/error rows for the summary table.
    with upload_tab:
        st.subheader("Upload documents")
        uploaded_files = st.file_uploader(
            "Select one or more documents",
            type=list(DEFAULT_ALLOWED_EXTENSIONS),
            accept_multiple_files=True,
        )

        if uploaded_files:
            with st.spinner("Processing uploads..."):
                LOGGER.info("Processing %d uploaded file(s).", len(uploaded_files))
                for uploaded_file in uploaded_files:
                    detail: Dict[str, object] = {"name": uploaded_file.name}
                    try:
                        LOGGER.debug("Saving uploaded file %s", uploaded_file.name)
                        saved_path = save_uploaded_file(uploaded_file)
                        ingestion_result = ingest_file_from_path(saved_path)
                        detail.update({"status": "success", "result": ingestion_result})
                        LOGGER.info("Ingested %s successfully", uploaded_file.name)
                    except Exception as exc:  # Broad catch to surface errors in the UI.
                        detail.update({"status": "error", "error": str(exc)})
                        LOGGER.exception("Failed to ingest uploaded file %s", uploaded_file.name)
                    ingestion_details.append(detail)

            st.toast("Upload complete.")

        if ingestion_details:
            st.subheader("Ingestion summary")
            success_entries = [d for d in ingestion_details if d.get("status") == "success"]
            error_entries = [d for d in ingestion_details if d.get("status") == "error"]

            if success_entries:
                st.success(f"Ingested {len(success_entries)} file(s) successfully.")
                success_table = [
                    {
                        "file_id": detail["result"]["file_id"],
                        "name": detail["result"]["name"],
                        "extension": detail["result"]["extension"],
                        "size_bytes": detail["result"]["size_bytes"],
                        "path": detail["result"]["path"],
                    }
                    for detail in success_entries
                ]
                LOGGER.debug("Rendering %d success entries.", len(success_entries))
                st.dataframe(success_table, use_container_width=True)

            if error_entries:
                st.error(f"Failed to ingest {len(error_entries)} file(s).")
                for detail in error_entries:
                    st.warning(f"{detail['name']}: {detail['error']}")
                LOGGER.warning("Encountered %d ingestion failure(s).", len(error_entries))

    # Refresh current directory contents every rerun so the data tab stays live.
    files_metadata, message, is_error = get_existing_files_metadata()
    with existing_tab:
        render_existing_files(files_metadata, message, is_error)


if __name__ == "__main__":
    main()
