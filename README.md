# IP-SAKTI Sahayak

**IP-SAKTI Sahayak** is a research-support prototype for Ayurveda, traditional knowledge, and intellectual property. It helps users explore Indian patentability and biodiversity rules, ASU regulatory material, and selected international instruments using a searchable local knowledge base with linked source citations.

This project is submitted by **Team OUTLAWS** for Smart India Hackathon 2026, Problem Statement **SIH26045**. The codebase retains the internal project name **DrugVista** in some package names and configuration.

## What the prototype does

- Answers questions using a curated corpus of legal, regulatory, and traditional-knowledge references.
- Retrieves relevant passages and presents source links and citation anchors for review.
- Routes questions across Indian and international sources and supports English, Hindi, and Kannada interactions.
- Includes research flows for patentability and prior-art triage, biological-resource access and benefit sharing, and Ayurveda/ASU regulatory frameworks.
- Runs with a local retrieval stack; an OpenAI-compatible model endpoint can be enabled through environment variables.

The prototype is for research support and educational use. It does not provide legal advice, determine patentability, or replace advice from a qualified professional. Check cited primary sources and current rules before relying on an answer.

## Architecture

```text
Streamlit interface  →  FastAPI service  →  Retrieval and reasoning
                                         ├─ FAISS vector index
                                         ├─ SQLite metadata store
                                         └─ Local knowledge corpus and source manifest
```

The application code and its data live in [`drugvista/`](drugvista/). The top-level `data/` and `docs/` directories contain repository-level materials. Final SIH hand-in files are grouped in [`submission/`](submission/), while editable presentation sources and assets are in [`presentation/`](presentation/).

## Run locally

### Requirements

- Python 3.10 or newer
- Packages listed in [`drugvista/requirements.txt`](drugvista/requirements.txt)
- The bundled knowledge corpus and vector index under `drugvista/data/` and `drugvista/storage/`

From the repository root, create and activate a virtual environment, then install the application requirements:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r drugvista/requirements.txt
```

Start the API in one terminal:

```bash
cd drugvista/backend
python -m uvicorn main:app --reload --port 8000
```

Start the interface in a second terminal:

```bash
cd drugvista/frontend
python -m streamlit run app.py --server.port 8501
```

Open [http://localhost:8501](http://localhost:8501). The API health endpoint is [http://localhost:8000/health](http://localhost:8000/health).

The UI reads `BACKEND_URL` and defaults to `http://localhost:8000`. The backend stores its FAISS index and SQLite database under `drugvista/storage/` by default. If rebuilding the index, use the project's ingestion and embedding utilities from `drugvista/backend/embeddings.py`; the sentence-transformers embedding model may need to be downloaded on first use.

## Optional model endpoint

Without a valid API key, the backend uses its offline rule-based provider. To enable a remote OpenAI-compatible model, set these environment variables before starting the backend:

```text
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
```

When configured, prompts may be sent to that endpoint. Use a provider and deployment appropriate for your data-handling requirements. Leave the key unset to use the offline provider.

## Repository map

| Path | Purpose |
| --- | --- |
| `drugvista/frontend/` | Streamlit user interface |
| `drugvista/backend/` | FastAPI service, retrieval, classification, reasoning, and language support |
| `drugvista/data/knowledge/` | Source corpus, manifests, and evaluation datasets |
| `drugvista/storage/` | SQLite metadata database and FAISS vector index |
| `tests/` | Automated test suite |
| `docs/` | Application and knowledge-base documentation |
| `presentation/` | Editable deck source, assets, generation scripts, and working previews |
| `submission/` | Final presentation and project report files |

## Project references

- [SIH 2026 project report](submission/SIH2026_PROJECT_REPORT_OUTLAWS.md)
- [Submission-ready presentation](submission/IP-SAKTI_Sahayak_SIH2026_submission_ready.pptx)
- [Submission PDF](submission/IP-SAKTI_Sahayak_SIH2026_outlaws.pdf)
- [Knowledge base notes](drugvista/data/knowledge/README.md)
- [Source repository](https://github.com/Rengoku9000/ip-shakti)
- [Project dossier](https://drive.google.com/drive/folders/1nfDT2fVEXlzJ61C37zGnA_zNBlg5g-mK?usp=sharing)
