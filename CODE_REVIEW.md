# Code Review

## Project Overview
- The repository provides a lightweight document ingestion playground with a CLI runner and Streamlit UI for uploading PDF, TXT, DOCX, CSV, or XLSX files into a normalized metadata structure, with future hooks for orchestration agents. 【F:README.md†L1-L38】

## Strengths
- Logging is centralized via `configure_run_logger`, which resets handlers and writes both console and file output into per-run directories, giving reproducible logs across the CLI and UI entry points. 【F:src/core/logging_utils.py†L18-L61】
- The ingestion agent consistently normalizes metadata (ID, name, extension, source, path, size) and is reused by both runtimes, improving parity between the CLI and Streamlit flows. 【F:src/agents/ingestion_agent/ingestion_agent.py†L21-L111】【F:main.py†L20-L60】【F:ui/app.py†L102-L165】

## Issues and Risks
1. **CLI run stops on the first ingest failure.** `run_ingestion` does not isolate per-file errors; any exception from `ingest_file_from_path` will bubble up and halt the loop, so one bad file prevents the rest of the directory from being processed. 【F:main.py†L31-L50】
2. **Potential memory pressure from unbounded file reads.** `ingest_file_from_path` reads each file fully into memory and stores the raw bytes in the result without size checks or streaming, which can exhaust memory or slow the UI when large uploads slip through. 【F:src/agents/ingestion_agent/ingestion_agent.py†L73-L111】
3. **Uploads can overwrite existing files and lack server-side validation.** The Streamlit flow writes uploaded files using the original filename directly into `input/` without collision protection or size/extension checks beyond the client hint, so users can accidentally overwrite prior uploads or upload unexpectedly large/unsupported content. 【F:ui/app.py†L42-L133】

## Recommendations
- Wrap per-file ingestion in `run_ingestion` with try/except so failures are logged and the loop continues, optionally returning a success/error summary for callers. 【F:main.py†L31-L60】
- Add safeguards to ingestion (size thresholds, streaming/chunking, or configurable limits) and avoid storing raw `content_bytes` when not required, especially for large binaries. 【F:src/agents/ingestion_agent/ingestion_agent.py†L87-L109】
- Harden the upload path by de-duplicating filenames (e.g., prepend a timestamp/UUID), validating extensions and maximum size server-side, and surfacing any rejected uploads back to the UI. 【F:ui/app.py†L42-L159】
