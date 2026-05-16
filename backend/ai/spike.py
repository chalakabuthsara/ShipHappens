"""
PBI-04 spike — proves the full google-genai pattern end-to-end.

Usage (from the ShipHappens/backend/ directory):
    uv run python -m ai.spike                          # uses first PDF found
    uv run python -m ai.spike path/to/paper.pdf        # explicit path

The script:
  1. Uploads the PDF via the Gemini Files API.
  2. Calls generate_content with a Pydantic response_schema.
  3. Parses and validates the returned JSON.
  4. Saves the raw response to backend/ai/samples/spike_output.json.

Exit code 0 = success.  Anything else = something to fix before PBI-07.
"""

import json
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load .env before any module that reads env vars at import time.
# Using the absolute path so this works regardless of cwd.
# override=True replaces any shell env var that is set but empty.
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=True)

from google.genai import types  # noqa: E402 — must come after load_dotenv
from pydantic import BaseModel  # noqa: E402

from ai.client import client, fast_model  # noqa: E402 — must come after load_dotenv

# ── Locate a sample PDF ────────────────────────────────────────────────────
SAMPLES_DIR = Path(__file__).parent / "samples" / "source"


def _find_pdf(explicit: Optional[str] = None) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.exists():
            sys.exit(f"[spike] File not found: {p}")
        return p

    pdfs = list(SAMPLES_DIR.glob("*.pdf"))
    if not pdfs:
        sys.exit(
            f"[spike] No PDFs found in {SAMPLES_DIR}.\n"
            "       Drop at least one A-Level English paper there and re-run."
        )
    print(f"[spike] Using: {pdfs[0].name}")
    return pdfs[0]


# ── Pydantic schema for the spike (minimal — just proves the pattern) ──────
class SectionSummary(BaseModel):
    title: str
    question_types: list[str]
    marks: int


class PaperSummary(BaseModel):
    exam_title: str
    board: str
    total_marks: int
    duration_minutes: int
    sections: list[SectionSummary]


# ── Main spike logic ───────────────────────────────────────────────────────
def run(pdf_path: Path) -> PaperSummary:
    # Step 1 — upload the PDF to Gemini Files API
    print(f"[spike] Uploading {pdf_path.name} to Gemini Files API…")
    uploaded_file = client.files.upload(
        file=str(pdf_path),
        config=types.UploadFileConfig(mime_type="application/pdf"),
    )
    print(f"[spike] Uploaded → {uploaded_file.uri}")

    # Step 2 — call generate_content with a structured schema
    prompt = (
        "You are an exam-paper analyst. "
        "Analyse the uploaded past paper and return a structured summary. "
        "Return ONLY valid JSON matching the schema — no markdown, no explanation."
    )

    print(f"[spike] Calling {fast_model} with response_schema=PaperSummary…")
    response = client.models.generate_content(
        model=fast_model,
        contents=[uploaded_file, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=PaperSummary,
        ),
    )

    raw_text = response.text
    print(f"[spike] Raw response ({len(raw_text)} chars):\n{raw_text}\n")

    # Step 3 — parse and validate
    summary = PaperSummary.model_validate_json(raw_text)
    print(f"[spike] Parsed successfully:")
    print(f"        Title   : {summary.exam_title}")
    print(f"        Board   : {summary.board}")
    print(f"        Marks   : {summary.total_marks}")
    print(f"        Duration: {summary.duration_minutes} min")
    print(f"        Sections: {[s.title for s in summary.sections]}")

    # Step 4 — save raw output for FE mocking and debugging
    output_path = Path(__file__).parent / "samples" / "spike_output.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(json.loads(raw_text), indent=2), encoding="utf-8"
    )
    print(f"\n[spike] Raw JSON saved to {output_path}")

    return summary


if __name__ == "__main__":
    pdf_arg = sys.argv[1] if len(sys.argv) > 1 else None
    pdf = _find_pdf(pdf_arg)
    result = run(pdf)
    print("\n[spike] ✓ All checks passed — SDK pattern confirmed.")
