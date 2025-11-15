# ai-doc-agent

A lightweight playground for experimenting with document ingestion agents. The project currently focuses on:

- discovering supported files (`pdf`, `txt`, `docx`, `csv`, `xlsx`) inside the `input/` directory,
- turning each file into a normalized ingestion dictionary, and
- providing a Streamlit UI for uploading documents into the ingestion workflow.

## Flow Overview

1. **File discovery** – `src/agents/ingestion_agent/ingestion_agent.py` validates the `input/` folder, filters by allowed extensions, and orders the results for deterministic runs.
2. **Ingestion** – every supported file is read into memory, enriched with metadata (file ID, size, origin, path), and returned to the caller.
3. **Runtimes** – `main.py` provides a CLI orchestrator that ingests whatever already lives in `input/`, while `ui/app.py` exposes a Streamlit interface for interactive uploads.
4. **Future orchestration** – stubs in `src/core/orchestrator.py` and `app.py` are ready to host parsing/summarisation agents as the workflow grows.

## Getting Started

```bash
pip install -r requirements.txt
```

### Command-line run

```bash
python main.py
```

### Streamlit UI

```bash
streamlit run ui/app.py
```

The UI lets you upload supported file types; each upload immediately persists to `input/` and runs through the ingestion agent so you can observe the metadata that would flow into downstream steps.

## Logging Strategy

Every runtime configures a run-specific log folder via `src/core/logging_utils.py`. Logs land under `logs/<YYYYMMDD>/<app>_<timestamp>/<app>_<timestamp>.log`, and the Streamlit sidebar surfaces the live log path so you can tail a run while experimenting.

