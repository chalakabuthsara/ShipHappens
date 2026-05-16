# AI Module — `backend/ai/`

This module owns all three Gemini calls made by the ShipHappens backend.
Each call uses **Gemini structured output** (`response_schema`) so the model
is constrained to return valid JSON — no markdown fences, no hallucinated fields.

---

## 1. How to upload a PDF via the Files API

```python
from google.genai import types
from ai.client import client

uploaded = client.files.upload(
    file="/path/to/paper.pdf",
    config=types.UploadFileConfig(mime_type="application/pdf"),
)

# uploaded.uri  → "files/abc123"  (stable reference for subsequent calls)
# uploaded.name → "files/abc123"
```

**Key points:**
- Upload once per PDF, cache the resulting URI on the `SourceFile` DB row
  (`SourceFile.gemini_file_uri`). Never upload the same file twice.
- Uploaded files persist in the Files API for 48 hours. Re-upload if the
  `gemini_file_uri` returns a 404.
- Always pass `mime_type="application/pdf"` explicitly — the SDK does not
  sniff it reliably on Windows.

---

## 2. How to call `generate_content` with a Pydantic schema

```python
from google.genai import types
from pydantic import BaseModel
from ai.client import client, fast_model

class MySchema(BaseModel):
    field_a: str
    field_b: list[str]

response = client.models.generate_content(
    model=fast_model,                    # or pro_model for full paper gen
    contents=[uploaded_file, "Your prompt here."],
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=MySchema,        # Pydantic class, not an instance
    ),
)

result = MySchema.model_validate_json(response.text)
```

**Key points:**
- Pass the Pydantic *class* (not an instance) to `response_schema`.
- The model returns `response.text` as a raw JSON string — always
  use `.model_validate_json()` to parse and validate in one step.
- Use `fast_model` (`gemini-2.5-flash`) for blueprint extraction and
  per-question regeneration. Use `pro_model` (`gemini-2.5-pro`) for
  full-paper generation only (slower but higher quality).
- Pass file references *before* the prompt text in `contents`.

---

## 3. The retry-on-parse-failure pattern

All three prompts use the shared wrapper in `backend/ai/wrapper.py`
(built in PBI-19). The pattern:

```python
from ai.wrapper import call_structured
from ai.client import fast_model

result = call_structured(
    model=fast_model,
    contents=[uploaded_file, prompt],
    schema=MySchema,
    retries=1,       # one automatic retry on ValidationError or JSONDecodeError
)
```

Internally `call_structured` does:
1. Call `generate_content` with the schema.
2. Try `schema.model_validate_json(response.text)`.
3. On failure: log `response.text` at WARNING level, then retry once with a
   stricter system instruction ("Return ONLY JSON, no explanation").
4. On second failure: raise `ValueError` with the raw text attached so the
   route handler can return a 502 with a debug payload.

**During PBI-04 and PBI-07:** use the inline pattern from section 2 above.
Swap to `call_structured` in PBI-19 once the wrapper exists.

---

## 4. Running the spike

```bash
# from ShipHappens/backend/
uv run python -m ai.spike                     # auto-finds first PDF in samples/source/
uv run python -m ai.spike path/to/paper.pdf   # explicit path
```

Expected output:
```
[spike] Using: paper_2024.pdf
[spike] Uploading paper_2024.pdf to Gemini Files API…
[spike] Uploaded → files/abc123
[spike] Calling gemini-2.5-flash with response_schema=PaperSummary…
[spike] Raw response (312 chars): { ... }
[spike] Parsed successfully:
        Title   : A-Level English Literature Paper 1
        Board   : Cambridge
        Marks   : 75
        Duration: 120 min
        Sections: ['Section A — Unseen Poetry', 'Section B — Set Texts']
[spike] Raw JSON saved to ai/samples/spike_output.json
[spike] ✓ All checks passed — SDK pattern confirmed.
```

---

## 5. File map

| File | Purpose |
|---|---|
| `client.py` | Singleton `client`, `pro_model`, `fast_model` — import from here |
| `schemas.py` | `BlueprintSchema`, `PaperSchema`, `QuestionSchema` Pydantic models |
| `blueprint.py` | `extract_blueprint(file_uris)` → `BlueprintSchema` |
| `generate.py` | `generate_paper(blueprint, file_uris)` → `PaperSchema` |
| `regenerate.py` | `regenerate_question(paper, blueprint, qid, nudge?)` → `QuestionSchema` |
| `wrapper.py` | `call_structured(model, contents, schema, retries)` |
| `spike.py` | PBI-04 end-to-end proof of concept |
| `samples/source/` | Drop test PDFs here (gitignored) |
| `samples/spike_output.json` | Raw spike response — useful for debugging |
| `samples/blueprint_*.json` | Sample blueprint outputs (committed — FE mocks from these) |
| `samples/paper_*.json` | Sample paper outputs (committed — FE mocks from these) |
