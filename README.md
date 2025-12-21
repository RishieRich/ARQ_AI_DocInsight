# ai-doc-agent

A lightweight playground for experimenting with document ingestion agents. The project currently focuses on:

- discovering supported files (`pdf`, `txt`, `docx`, `csv`, `xlsx`) inside the `input/` directory,
- turning each file into a normalized ingestion dictionary, and
- providing a Streamlit UI for uploading documents into the ingestion workflow.

## Quickstart

**Prerequisites**

- Python 3.10+
- `pip` for dependency installation

**Install dependencies**

```bash
pip install -r requirements.txt
```

**Run the CLI ingestion workflow**

```bash
python main.py
```

The CLI scans the `input/` directory for supported files, ingests them sequentially, and emits run-scoped logs describing each decision.

**Run the Streamlit UI**

```bash
streamlit run ui/app.py
```

The UI lets you upload supported file types; each upload immediately persists to `input/` and runs through the ingestion agent so you can observe the metadata that would flow into downstream steps. The “Input Folder Overview” tab shows everything currently queued in `input/`.

## How the ingestion flow works

1. **File discovery** – `src/agents/ingestion_agent/ingestion_agent.py` validates the `input/` folder, filters by allowed extensions, and orders the results for deterministic runs.
2. **Ingestion** – every supported file is read into memory, enriched with metadata (file ID, size, origin, path), and returned to the caller.
3. **Runtimes** – `main.py` provides a CLI orchestrator that ingests whatever already lives in `input/`, while `ui/app.py` exposes a Streamlit interface for interactive uploads.
4. **Future orchestration** – stubs in `src/core/orchestrator.py` and `app.py` are ready to host parsing/summarisation agents as the workflow grows.

## Supported files and configuration

- Default extensions: `pdf`, `txt`, `docx`, `csv`, `xlsx` (`DEFAULT_ALLOWED_EXTENSIONS` in `src/agents/ingestion_agent/ingestion_agent.py`).
- Files are read from and written to `input/`. Delete or replace files there to control what the agent ingests.
- Both entry points normalise metadata into a dictionary with ID, extension, source, path, size, and raw bytes so downstream agents can plug in without re-reading the file system.

## Logging strategy

Every runtime configures a run-specific log folder via `src/core/logging_utils.py`. Logs land under:

```
logs/<YYYYMMDD>/<app>_<YYYYMMDD_HHMMSS>/<app>_<YYYYMMDD_HHMMSS>.log
```

The Streamlit sidebar surfaces the live log path, and the CLI echoes it at startup, so you can tail the file while experimenting.
