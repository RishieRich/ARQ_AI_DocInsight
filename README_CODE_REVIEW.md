# AI Doc Agent – Code Review (2025-12-23)

This document records a static code review of the repository as of **2025-12-23**. The review covers structure, correctness, reliability, and maintainability based on the current source tree. No dynamic tests were executed.

## Scope and approach

- Read-through of core modules: CLI (`main.py`), Streamlit UI (`ui/app.py`), ingestion helpers (`src/agents/ingestion_agent/ingestion_agent.py`), and logging utilities (`src/core/logging_utils.py`).
- Light inspection of auxiliary files and LLM sanity-check scripts in `llm_tests/`.
- Focused on correctness, failure modes, and developer experience.

## Architecture snapshot

- **Entry points**: `main.py` drives CLI ingestion; `ui/app.py` provides a Streamlit UI that shares ingestion helpers.
- **Ingestion agent**: `src/agents/ingestion_agent/ingestion_agent.py` lists allowed files from `input/` and normalizes them into metadata dictionaries (including `content_bytes`).
- **Logging**: `src/core/logging_utils.py` centralizes run-scoped logging with per-run log folders.
- **Future expansion**: `src/core/orchestrator.py` and `app.py` are placeholders for additional runtimes or orchestration logic.

## Strengths

- **Deterministic ingestion order** by sorting discovered files, aiding reproducibility.
- **Run-scoped logging** with consistent directory layout, and handler reset to avoid duplicate log outputs across reruns.
- **UI/CLI reuse** of ingestion helpers keeps behavior consistent between runtimes.
- **Clear metadata contract** returned from ingestion (`file_id`, `extension`, `size_bytes`, `content_bytes`, etc.), making downstream processing straightforward.

## Findings and recommendations

1) **Uploaded files overwrite existing inputs without warning**  
   - `save_uploaded_file` writes uploads directly to `input/<filename>` without checking for existing files, so a second upload with the same name silently replaces prior data. Overwrites can hide previous test cases and make ingestion results non-reproducible.  
   - **Recommendation**: Refuse or rename on collision (e.g., append timestamp/UUID) and surface the outcome in the UI so users know whether a file was replaced.

2) **No guardrails on file size or streaming**  
   - `ingest_file_from_path` reads the entire file into memory and attaches `content_bytes` to the returned dict. Large PDFs/CSVs will be fully loaded and duplicated in memory when displayed in the UI, risking OOM for big uploads.  
   - **Recommendation**: Enforce a configurable size limit and stream large files (or omit `content_bytes` for UI display), returning a handle/path instead for downstream processors.

3) **Ingestion run stops on the first per-file error (CLI)**  
   - `run_ingestion` processes files sequentially but does not isolate failures; any exception from `ingest_file_from_path` aborts the entire run, leaving later files unprocessed without visibility into which ones were skipped.  
   - **Recommendation**: Catch per-file exceptions, log them, and continue with remaining files. Return both successes and failures so callers can summarize the run comprehensively.

4) **UI error surfacing is coarse and lacks remediation guidance**  
   - The Streamlit UI collapses ingestion failures into a simple warning string per file, without distinguishing common causes (unsupported extension, missing directory, size limits, etc.) or offering follow-up actions.  
   - **Recommendation**: Categorize errors (validation vs. I/O vs. parsing) and provide actionable messages (e.g., “Unsupported extension .md; allowed: pdf, txt, docx, csv, xlsx”).

5) **Limited validation and safety checks for ingestion inputs**  
   - Allowed extensions are enforced, but there is no MIME-type verification, path sanitization, or empty-file handling. The UI writes uploaded filenames verbatim, which could introduce unexpected characters.  
   - **Recommendation**: Normalize filenames (strip path separators/control chars), optionally verify MIME type, and reject zero-length files with a clear error.

6) **Operational gaps and missing automation**  
   - No automated tests cover ingestion behavior (e.g., sorting, extension filtering, error cases), and LLM sanity-check scripts depend on external services without guards in `requirements.txt` for `ollama`.  
   - **Recommendation**: Add unit tests around `list_input_files` and `ingest_file_from_path`, stub file fixtures, and document optional dependencies or mark those scripts as “manual/optional” to avoid breakage.

## Quick-win backlog (ordered)

1. Add collision-safe upload handling and surface messages in the Streamlit UI.  
2. Introduce a configurable max file size and avoid attaching raw `content_bytes` for large files.  
3. Make CLI ingestion fault-tolerant per file and summarize successes/failures.  
4. Harden filename/MIME validation and reject empty files early.  
5. Add unit tests for ingestion helpers and document optional LLM test dependencies.

## Notes on testing

No tests were run during this review; recommendations above include suggested coverage to implement.
