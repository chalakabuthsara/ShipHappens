# ShipHappens — Smart Paper Generator
## MVP Build Plan · 20-Hour Buildathon

> **Demo subject:** A-Level English · **Architecture:** subject-agnostic  
> **Team:** 1 AI Engineer · 1 Full-Stack Backend Lead (FS1) · 1 Full-Stack Data Lead (FS2) · 1 Frontend Engineer (FE)

---

## Stack

| Layer | Choice |
|---|---|
| Frontend | Next.js 14 (App Router) + TypeScript + Tailwind + shadcn/ui |
| Backend | FastAPI + Uvicorn + SQLModel + Pydantic v2 |
| Database | Supabase (managed Postgres, no docker needed) |
| File storage | Supabase Storage — private bucket `uploads` |
| AI | `google-genai` SDK · `gemini-2.5-pro` (paper gen) + `gemini-2.5-flash` (blueprint + regen) |
| PDF export | Server-rendered HTML via Jinja2 + browser `window.print()` |

**What we dropped from the original `pyproject.toml`:** `pgvector`, `alembic`.  
**What we added:** `supabase` Python client, `jinja2`.

---

## What's In / What's Out

**In scope:**
- Upload 3–5 past papers → extract structural blueprint → generate new paper
- Per-question text editing in the browser with autosave
- Per-question regeneration with optional nudge text
- Export to PDF via browser print

**Out of scope for this MVP:**
- Authentication or multi-user sessions
- Vector search / RAG / embeddings
- Server-side PDF generation (WeasyPrint is a stretch goal only)
- Per-section regeneration
- Paper history / saved sessions across days

---

## User Flow

```
Upload (3-5 PDFs) → Blueprint Review → Editable Paper → PDF Export
                                             ↑___regenerate question___↑
```

1. **Upload** — Drag-drop 3–5 PDFs, optional title/board/level/subject fields, click "Analyze".
2. **Blueprint Review** — Read-only view of extracted structure: sections, marks, question types, instructions, tone notes. Single "Generate New Paper" CTA.
3. **Editable Paper** — Each question is an editable card. Auto-growing textarea, marks field, "Regenerate" button per question (with optional nudge input). Autosave debounced 800ms.
4. **PDF Export** — iframe preview of the formatted paper + "Download PDF" button triggering `window.print()`.

---

## Architecture

```
Browser (Next.js)
    └── Wizard UI (4 pages) + Zustand store
         └── fetch (credentials: include, sid cookie)
              └── FastAPI Backend
                   ├── routes/  (sessions, upload, blueprint, generate, paper, export)
                   ├── ai/      (blueprint.py, generate.py, regenerate.py)
                   ├── storage.py  → Supabase Storage + Gemini Files API cache
                   ├── db/models.py → SQLModel → Supabase Postgres
                   └── templates/paper.html.j2 → print CSS → /export.html
                        ├── Google Gemini API (3 calls per session)
                        └── Supabase (Postgres + Storage)
```

---

## Data Models

### SQLModel tables (`backend/db/models.py`)

```python
class Session(SQLModel, table=True):
    id: UUID               # primary key, also the cookie value
    created_at: datetime
    title: str | None
    board: str | None      # "Cambridge", "AQA", "Edexcel", "OCR"
    level: str | None      # "A Level", "AS Level"
    subject: str | None    # "English Literature"

class SourceFile(SQLModel, table=True):
    id: UUID
    session_id: UUID       # FK → Session
    filename: str
    storage_path: str      # uploads/{session_id}/{file_uuid}.pdf
    gemini_file_uri: str | None   # cached — upload once, reuse always

class Paper(SQLModel, table=True):
    id: UUID
    session_id: UUID       # FK → Session (unique)
    blueprint_json: dict   # BlueprintSchema
    paper_json: dict       # PaperSchema
    updated_at: datetime
```

### Blueprint JSON shape (AI output, locked after PBI-07)

```json
{
  "subject": "English Literature",
  "board": "Cambridge",
  "level": "A Level",
  "duration_minutes": 180,
  "total_marks": 100,
  "tone_notes": "Formal academic register...",
  "instructions_pattern": ["Answer all questions.", "..."],
  "sections": [
    {
      "id": "secA",
      "title": "Section A — Drama",
      "marks": 25,
      "instructions": "Answer one question.",
      "question_types": ["essay"],
      "typical_prompt_style": "Compare and contrast..."
    }
  ]
}
```

### Paper JSON shape (AI output + user-editable, locked after PBI-11)

```json
{
  "title": "A-Level English Literature — Mock Paper",
  "duration_minutes": 180,
  "total_marks": 100,
  "instructions": ["Answer all questions.", "Time: 3 hours."],
  "sections": [
    {
      "id": "secA",
      "title": "Section A — Drama",
      "marks": 25,
      "instructions": "Answer one question.",
      "questions": [
        {
          "id": "q1",
          "number": "1",
          "marks": 25,
          "type": "essay",
          "prompt": "Discuss how Shakespeare presents...",
          "sub_parts": [],
          "context_passage": null
        }
      ]
    }
  ]
}
```

> **Rule:** `question.id` is stable for the life of the paper. Regeneration replaces the content but keeps the id. The frontend uses it as the React key. The backend uses it to splice. **Do not rename these fields after they are locked.**

---

## API Endpoints

| Method | Path | Owner | Notes |
|---|---|---|---|
| `POST` | `/sessions` | FS1 | Creates session row, sets `sid` cookie |
| `POST` | `/sessions/{id}/upload` | FS1 + FS2 | Multipart PDFs; saves to Supabase Storage + Gemini Files |
| `POST` | `/sessions/{id}/blueprint` | FS1 + AI | Calls `extract_blueprint`, persists, returns blueprint |
| `POST` | `/sessions/{id}/generate` | FS1 + AI | Calls `generate_paper`, persists, returns full paper |
| `PUT` | `/sessions/{id}/paper` | FS1 + FS2 | Validates + saves user edits |
| `POST` | `/sessions/{id}/questions/{qid}/regenerate` | FS1 + AI | Replaces one question, returns it |
| `GET` | `/sessions/{id}/paper/export.html` | FS1 + FS2 | Jinja2-rendered print HTML |
| `GET` | `/sessions/{id}` | FS1 | Resume support — returns session + blueprint + paper |
| `GET` | `/healthz` | FS1 | Liveness check: DB + Gemini |

---

## AI Prompting Strategy

Three Gemini calls per session, all using `response_schema` (structured output — no markdown, no fences, just JSON):

1. **Blueprint extraction** (`gemini-2.5-flash`)  
   Input: 3–5 PDFs via Files API.  
   Output: `BlueprintSchema` — sections, marks, question types, instructions, tone notes.

2. **Paper generation** (`gemini-2.5-pro`)  
   Input: blueprint JSON + same PDFs (reused via cached `gemini_file_uri`).  
   Output: full `PaperSchema`. Hard constraints: marks must sum to blueprint total, every question id unique.

3. **Per-question regeneration** (`gemini-2.5-flash`)  
   Input: blueprint + current paper + target question id + optional nudge.  
   Output: single `QuestionSchema` replacement.

Each prompt uses a shared retry wrapper (`backend/ai/wrapper.py`) that retries once on parse failure and logs raw text for debugging.

---

## Environment Variables

### Backend (`backend/.env`)

```
GOOGLE_API_KEY=
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
SUPABASE_DB_URL=
SUPABASE_BUCKET=uploads
GEMINI_GENERATION_MODEL=gemini-2.5-pro
GEMINI_FAST_MODEL=gemini-2.5-flash
CORS_ORIGIN=http://localhost:3000
SESSION_COOKIE_NAME=sid
```

### Frontend (`front/.env.local`)

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Running locally

```bash
# Backend
cd ShipHappens/backend
uv sync
uv run uvicorn main:app --reload      # → http://localhost:8000
# OpenAPI docs at http://localhost:8000/docs

# Frontend
cd ShipHappens/front
npm install
npm run dev                           # → http://localhost:3000
```

---

## 20-Hour Task Allocation

### Phase 0 — h0 to h2 — Everyone scaffolds in parallel

| Who | Task |
|---|---|
| **FS2** | **Do this FIRST (h0–h1):** Create Supabase project + `uploads` bucket. Share URL + service key + DB connection string in pinned chat within 30 minutes. Everything else is blocked on this. |
| **FS1** | FastAPI app skeleton (`main.py`, `config.py`, CORS, session cookie middleware). Remove `pgvector` + `alembic` from `pyproject.toml`, add `supabase` + `jinja2`. Run `uv sync`. Verify server boots. |
| **FS2** | SQLModel models (`Session`, `SourceFile`, `Paper`) → `backend/db/models.py`. Engine pointed at Supabase. `create_all()` on startup. Commit `.env.example`. |
| **AI** | Gemini SDK spike: upload one sample PDF via Files API, call `generate_content` with a Pydantic `response_schema`, print JSON. Commit to `backend/ai/spike.py`. |
| **FE** | `npx create-next-app` + shadcn/ui + install `zustand swr react-dropzone`. Wizard layout with 4-step progress bar. Four empty route pages. Zustand store + typed API wrapper stub. |

---

### Phase 1 — h2 to h8 — Vertical Slice 1: Upload → Blueprint

**Milestone h8:** Demo "upload 3 PDFs → see blueprint on screen"

| Who | Task |
|---|---|
| **AI** | Blueprint extraction prompt in `backend/ai/blueprint.py`. Pydantic `BlueprintSchema`. Test against 2 sample PDF sets. Commit sample JSON outputs to `backend/ai/samples/` for FE mocking. |
| **FS2** | Storage adapter (`backend/storage.py`): upload PDF to Supabase Storage, push to Gemini Files API, cache `gemini_file_uri` on the `SourceFile` row. Idempotent. |
| **FS1** | `POST /sessions`, `POST /sessions/{id}/upload`, `POST /sessions/{id}/blueprint`. Wire to AI + Storage. File validation (PDF only, max 5, max 25 MB). |
| **FE** | Upload page (drag-drop, file list, "Analyze" button running 3-call chain). Blueprint review page (Accordion per section, "Generate" CTA). Mock with sample JSON from AI until FS1 endpoint is live. |
| **FS2** | `PaperSchema` + `QuestionSchema` Pydantic models in `backend/ai/schemas.py`. `splice_question(paper, question_id, new_question)` pure helper in `backend/utils/paper.py` with pytest coverage. |

---

### Phase 2 — h8 to h14 — Vertical Slice 2: Generate + Edit

**Milestone h14:** Demo "generate → edit any question → regenerate any question"

| Who | Task |
|---|---|
| **AI** | Paper generation prompt in `backend/ai/generate.py` (gemini-2.5-pro). Post-validate marks sum + unique ids. Commit sample paper JSON. Then: per-question regeneration prompt in `backend/ai/regenerate.py` (gemini-2.5-flash). |
| **FS1** | `POST /sessions/{id}/generate`, `PUT /sessions/{id}/paper`, `POST /sessions/{id}/questions/{qid}/regenerate`. 120s timeout on generate. |
| **FE** | Editable Paper page: section cards → question sub-cards → auto-grow Textarea + marks input + Regenerate button. `useAutosave` hook (debounced 800ms PUT). Skeleton during per-question regen. "Preview & Export" button. |
| **FS2** | Splice helper integration into regenerate endpoint. Server-side `validate_paper()` used in PUT. Support FS1 with integration. |

---

### Phase 3 — h14 to h18 — Vertical Slice 3: Export

**Milestone h18:** Demo "Download PDF → clean A4 paper in browser print dialog"

| Who | Task |
|---|---|
| **FS2** | Jinja2 template (`backend/templates/paper.html.j2`): cover page, sections, questions with marks in right margin, sub-parts (a)(b)(c), context-passage box. Print CSS: A4, serif, `page-break-inside: avoid`. |
| **FS1** | `GET /sessions/{id}/paper/export.html` endpoint (renders Jinja template). Next.js proxy route (`front/app/api/proxy/export.html/route.ts`) for same-origin iframe. |
| **FE** | Export page: iframe pointing to proxy route, "Download PDF" button calling `iframe.contentWindow.print()`, "Back to Edit" button. |
| **AI** | Prompt polish + shared retry wrapper (`backend/ai/wrapper.py`). Edge case hardening: 1-page PDFs, marks drift guard. |

---

### Phase 4 — h18 to h20 — Polish + Demo Prep

| Who | Task |
|---|---|
| **FS2** | `backend/seed.py` — inserts a demo session with pre-generated paper so live Gemini calls can be skipped. Smoke test script hitting every endpoint. |
| **FS1** | Global error handler (structured `{error: {code, message}}`), request logging middleware, beef up `/healthz`. |
| **FE** | Loading states on every button, sonner toasts on error, empty states, "Start over" reset link. |
| **AI** | Support demo dry runs, fix any prompt failures. |
| **Everyone** | Write demo script (5 min). Dry run twice. Record backup video. |

---

## Scope Cuts (invoke in this order if a milestone slips)

1. Drop per-section regenerate — keep per-question only.
2. Drop Blueprint Review step — route directly from Upload to generated Paper; show blueprint collapsed above.
3. Drop autosave — require explicit "Save" button instead.
4. Drop per-question regenerate — text edits only, no Gemini regen call.
5. Drop print CSS polish — plain HTML print is fine for demo.
6. Drop the nudge input on regenerate — just regenerate without it.

---

## Key Risks + Mitigations

| Risk | Mitigation |
|---|---|
| Gemini returns invalid JSON | `response_schema` + 1 retry + log raw text from h0 |
| Generate call takes 30–60s, UI looks frozen | Step indicator with "this can take a minute"; 120s backend timeout |
| Gemini Files API quota / errors | Cache `gemini_file_uri`; cap at 5 files; sequential uploads |
| Supabase creds wrong on someone's laptop | `.env.example` checked in; `/healthz` checks DB; FS2 shares in first 30 min |
| FE rebuilds rich-text from scratch | Hard rule: shadcn `Textarea` + auto-grow. No tiptap, no Slate, no contenteditable polish |
| Splice bug during regenerate | Pure function with unit tests; both AI and FS1 import FS2's helper — not duplicated |
| Demo machine fails live | `seed.py` provides fallback data; record backup video at h18 |

---

## Cross-Dev Dependencies (read before starting Phase 1+)

| Blocker | Blocked | Workaround |
|---|---|---|
| FS2 Supabase setup (h1) | FS1, AI, FE all need env vars | FS2 posts creds in chat within 30 min of h0 |
| AI `BlueprintSchema` sample JSON (h6) | FE Blueprint page | FE builds against sample JSON in `backend/ai/samples/`; swaps on h8 |
| AI `PaperSchema` sample JSON (h13) | FE Editable Paper page | FE builds against sample JSON; mock data in Zustand store during dev |
| FS2 Jinja template (h18) | FE Export page | FE shows a `<pre>` dump of paper JSON as placeholder; swaps on h18 |

---

## Repository Layout

```
ShipHappens/
├── front/                        ← FE owns
│   ├── app/(wizard)/
│   │   ├── layout.tsx            (wizard shell + progress bar)
│   │   ├── upload/page.tsx
│   │   ├── blueprint/page.tsx
│   │   ├── paper/page.tsx
│   │   └── export/page.tsx
│   ├── app/api/proxy/export.html/route.ts
│   ├── components/               (UploadDropzone, SectionCard, QuestionCard, PrintFrame)
│   ├── lib/store.ts              (Zustand)
│   ├── lib/api.ts                (typed fetch wrapper)
│   └── .env.local
└── backend/                      ← FS1 + FS2 + AI own
    ├── main.py                   ← FS1
    ├── config.py                 ← FS1
    ├── storage.py                ← FS2
    ├── ai/
    │   ├── client.py             ← AI
    │   ├── schemas.py            ← AI (BlueprintSchema, PaperSchema, QuestionSchema)
    │   ├── blueprint.py          ← AI
    │   ├── generate.py           ← AI
    │   ├── regenerate.py         ← AI
    │   ├── wrapper.py            ← AI
    │   └── samples/              ← AI (sample JSON for FE mocking)
    ├── db/
    │   ├── engine.py             ← FS2
    │   └── models.py             ← FS2
    ├── routes/
    │   ├── sessions.py           ← FS1
    │   ├── uploads.py            ← FS1
    │   ├── blueprint.py          ← FS1
    │   ├── generate.py           ← FS1
    │   ├── paper.py              ← FS1
    │   └── export.py             ← FS1
    ├── utils/
    │   └── paper.py              ← FS2 (splice_question, validate_paper)
    ├── templates/
    │   └── paper.html.j2         ← FS2
    ├── scripts/
    │   └── smoke.py              ← FS2
    ├── seed.py                   ← FS2
    ├── pyproject.toml
    ├── .env                      (gitignored)
    ├── .env.example
    └── data/
        ├── build.html            (architecture + API reference)
        ├── backlog.html          (PBI cards, subtasks, acceptance criteria)
        └── PLAN.md               (this file)
```

---

## Per-Developer Summary (copy to your chat / Notion)

### AI Engineer
Your files: `backend/ai/`  
h0–2: SDK spike · h2–8: Blueprint prompt · h8–13: Paper generation prompt · h13–14: Regeneration prompt · h14–16: Retry wrapper · h16–18: Edge case hardening · h18–20: Demo support

### Full-Stack 1 — Backend Lead
Your files: `backend/main.py`, `backend/routes/`  
h0–2: App scaffold · h2–8: Session + Upload + Blueprint endpoints · h8–14: Generate + Edit + Regenerate endpoints · h14–16: Export endpoint + proxy · h18–20: Error handling + health check

### Full-Stack 2 — Data Lead
Your files: `backend/db/`, `backend/storage.py`, `backend/utils/`, `backend/templates/`  
h0–1: **Supabase setup (FIRST)** · h1–2: DB models · h2–6: Storage adapter · h5–8: PaperSchema + splice helper · h14–18: Jinja template · h18–20: Seed data + smoke tests

### Frontend Engineer
Your files: `front/`  
h0–2: Next.js scaffold · h2–5: Upload page · h5–8: Blueprint page · h8–14: Editable Paper page · h14–18: Export page · h18–20: Loading + error states + polish

---

*Full architecture diagrams, sequence diagrams, and PBI subtask checklists: open `build.html` and `backlog.html` in a browser.*
