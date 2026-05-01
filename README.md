# RegIntel AI

Production-style but demo-friendly regulatory review system with a FastAPI backend and React frontend.

## Features

- File upload for `pdf`, `docx`, and `txt`
- Text parsing with section splitting
- Basic anonymization for patient identifiers
- Structured summarization stub shaped for LLM replacement
- Completeness rules engine
- Severity classification (rule-based hybrid starter)
- Version comparison with semantic-friendly field diffs
- Report persistence in SQLAlchemy
- Demo dataset with ground-truth labels, incomplete cases, and revised versions

## Run

Backend:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

API docs:

- `http://127.0.0.1:8000/docs`
- Frontend UI: `http://127.0.0.1:3000`

Health checks:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/api/v1/health`

## Endpoints

- `POST /api/v1/upload`
- `POST /api/v1/analyze`
- `POST /api/v1/compare`
- `GET /api/v1/report/{report_id}`
- `GET /api/v1/report/{report_id}/export/json`
- `GET /api/v1/report/{report_id}/export/pdf`
- `GET /api/v1/health`

## Frontend Screens

- Dashboard with `Total Cases`, `Incomplete Cases`, `High Severity Cases`, and `Pending Reviews`
- Upload / Analyze for `.txt` and `.pdf` submissions
- Review Results with case summary, completeness check, PII/PHI detection, severity classification, and officer recommendation
- Version Comparison with changed fields, impact column, and officer-facing summary
- Export Officer Packet actions for JSON and PDF

## Notes

- Default database is SQLite for zero-friction local demo use.
- Switch `DATABASE_URL` to PostgreSQL in `.env` for production-like deployment.
- LLM integration now supports local Ollama models, with `qwen2.5:7b` as the default structured-summary model.
- Structured demo assets live under `data/`.
- Root-level `sae_case_00x.txt` files remain available, but `data/sae_cases/` is the cleaner source-of-truth layout for demos.

## Ollama

Install and pull the default model:

```bash
ollama pull qwen2.5:7b
```

Run Ollama locally on the default host:

```bash
ollama serve
```

The backend reads:

- `LLM_PROVIDER=ollama`
- `LLM_MODEL=qwen2.5:7b`
- `OLLAMA_BASE_URL=http://127.0.0.1:11434`

If Ollama is unavailable, the backend falls back to a deterministic summary so the rest of the pipeline still works.

## Demo Data

- [data/sae_cases/sae_case_006_incomplete.txt](/home/vhits/RegIntel%20AI/data/sae_cases/sae_case_006_incomplete.txt) proves missing-field detection.
- [data/sae_cases/sae_case_001_revised.txt](/home/vhits/RegIntel%20AI/data/sae_cases/sae_case_001_revised.txt) supports comparison and version diff demos.
- [data/labels/sae_case_001.json](/home/vhits/RegIntel%20AI/data/labels/sae_case_001.json) through [data/labels/sae_case_001_revised.json](/home/vhits/RegIntel%20AI/data/labels/sae_case_001_revised.json) provide structured references for testing.
- Rule packs are available in [data/rules/sae_rules.json](/home/vhits/RegIntel%20AI/data/rules/sae_rules.json), [data/rules/clinical_trial_rules.json](/home/vhits/RegIntel%20AI/data/rules/clinical_trial_rules.json), [data/rules/device_rules.json](/home/vhits/RegIntel%20AI/data/rules/device_rules.json), [data/rules/ethics_rules.json](/home/vhits/RegIntel%20AI/data/rules/ethics_rules.json), and [data/rules/anonymization_rules.json](/home/vhits/RegIntel%20AI/data/rules/anonymization_rules.json).
- A concrete demo review output is included at [data/sample_outputs/sae_case_006_review_output.json](/home/vhits/RegIntel%20AI/data/sample_outputs/sae_case_006_review_output.json).

## Example Flow

Upload:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/upload" \
  -F "file=@sample_case.txt"
```

Analyze:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"report_id": 1}'
```

Compare:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/compare" \
  -H "Content-Type: application/json" \
  -d '{"source_report_id": 1, "target_report_id": 2}'
```

For best comparison results, analyze both reports before calling `/compare`.

Export JSON:

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/report/2/export/json?compare_to_report_id=1"
```

Export PDF:

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/report/2/export/pdf?compare_to_report_id=1" --output officer_packet.pdf
```
