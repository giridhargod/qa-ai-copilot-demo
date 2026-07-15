# Secure Test Step Generator (V1)

Turns a Word/PDF document containing SnagIt screenshots + tester notes into
an enterprise test-step Excel file (`Step No | Action | Expected Result |
Confidence | Confidence Reason | Warnings | Status`), without ever sending a
raw screenshot or unredacted sensitive data to an LLM.

```
Document -> OCR -> Sanitization -> AI Step Generation -> Validation -> Excel Export
```

This package is self-contained: it does not import anything from the rest of
the qa-ai-copilot repository, so it can be copied out and run on its own.

## Setup

1. Python 3.11+ and a working [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
   install on your PATH (required by `pytesseract` -- this is a system binary,
   `pip install` alone won't get it). Verify it's on PATH with:
   ```
   tesseract --version
   ```
2. From this folder:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in this folder (or export the variable) with:
   ```
   OPENAI_API_KEY=sk-...
   ```

## How to use

1. Prepare a `.docx` or `.pdf` test-evidence document: one or more pasted
   screenshots (e.g. from SnagIt), each optionally preceded by a short tester
   note. Screenshots inside table cells are supported.
2. Run the CLI from the directory **above** this one (so
   `secure_test_step_generator` is importable as a package):
   ```
   python -m secure_test_step_generator.cli --input path/to/document.docx --output path/to/folder
   ```
   `--input` accepts `.docx` or `.pdf`. `--output` is the exact folder the
   `.xlsx` file is written to (created if it doesn't exist).

   > Getting `No module named secure_test_step_generator`? You're running the
   > command from inside this folder instead of the folder above it.
3. Open the generated `<document-name>_test_steps.xlsx`. Each row is one
   screenshot, in document order, with:
   - **Action** / **Expected Result** -- the AI's read of what the tester did
     and what should happen, based only on the OCR text/notes/cursor hint for
     that screenshot.
   - **Confidence** -- the AI's own self-assessed confidence (0-100%); see
     "Known limitations" below.
   - **Warnings** -- anything a human reviewer should double check (thin
     evidence, low confidence with no stated reason, sensitive data caught and
     redacted, a possible prompt-injection attempt in the source evidence).
4. Treat every row as a draft. Rows with warnings or confidence below
   `STSG_LOW_CONFIDENCE_THRESHOLD` (60% by default) need a human pass before
   they're trusted as final test steps.

### Configuration (optional)

All of these are read from `.env` / the environment; every one has a working
default, so none are required.

| Variable | Default | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | *(none -- required)* | OpenAI API key used for step generation. |
| `STSG_OPENAI_MODEL` | `gpt-4o-mini` | Model passed to the OpenAI Chat Completions API. |
| `STSG_LOW_CONFIDENCE_THRESHOLD` | `0.6` | Confidence below this gets flagged for mandatory human review. |
| `STSG_CURSOR_HINT_MIN_CONFIDENCE` | `0.55` | Minimum score before the cursor-position heuristic reports a hint at all. |
| `STSG_OUTPUT_FILENAME` | `test_steps.xlsx` | Fallback filename when one can't be derived from the source document's name. |

## Security boundary

No image bytes, and no unsanitized text, are ever passed to the LLM.
`step_generator.py` (the only module that calls an LLM) only accepts
`SanitizedEvidenceItem` -- a type that structurally cannot carry raw image
bytes or unredacted text. `sanitizer.py` replaces (never deletes) sensitive
values with placeholders like `<SSN>`, `<CLAIMANT_ID>`, `<AMOUNT>` before
anything reaches that boundary. `validator.py` re-runs the same detectors
against the AI's own output as a defense-in-depth check.

`patterns.py`'s `KNOWN_INTERNAL_TERMS` list is empty by default -- project
names, internal application names, and environment/server names are
open-vocabulary and can't be regex-derived. **Populate this list with your
team's actual internal terms before pointing this at real project
documents.**

OCR text and tester notes are also the one input an attacker could realistically
shape (text baked into a screenshot, or typed directly), so they're treated as
untrusted the same way PII is: `patterns.INJECTION_PATTERNS` neutralizes common
prompt-injection phrasing (e.g. "ignore previous instructions", `<|im_start|>`)
into a `<POTENTIAL_INSTRUCTION>` placeholder before it reaches the LLM, and the
prompt template itself separately instructs the model to treat all evidence as
data, never as instructions. Neither layer is exhaustive on its own -- they're
deliberately redundant defense-in-depth, not a guarantee against every possible
rephrasing.

## Known limitations (V1)

- **Cursor-position hint is a best-effort heuristic**, not a trained
  detector (`ocr.py::detect_cursor_hint`). It looks for a small, isolated,
  high-contrast region and reports it only above a confidence floor;
  otherwise it reports nothing rather than guessing. It can be fooled by
  other small icons (checkboxes, logos) in the screenshot.
- **PDF note/screenshot pairing is page-granularity, not paragraph-granularity**
  (`document_reader.py::_extract_from_pdf`) -- a page's full text is attached
  as notes to the first screenshot found on that page. The `.docx` path is
  precise to the paragraph.
- Confidence scores and reasons come entirely from the LLM's own
  self-assessment; there is no independent deterministic confidence model in
  V1.
- **The sanitizer is deliberately tuned for high recall over high precision**
  (`patterns.py`): bare 9-digit numbers are always masked as `<SSN>`, and bare
  10-12 digit numbers as `<ID>`, with no surrounding context required. This
  is intentional for a security-first tool (a false "this looks like an SSN"
  costs a slightly noisier Excel cell; a missed real SSN is the actual risk
  this tool exists to prevent) -- but it means **non-enterprise numeric
  strings get masked too**, confirmed on realistic examples:
  - `"Order number 847293156 confirmed"` -> `"Order number <SSN> confirmed"`
  - `"Video ID appears in URL as 123456789"` -> `"...as <SSN>"`
  - `"Invoice #482910573 was generated"` -> `"Invoice #<SSN> was generated"`
  - `"...9048372910 ms total"` (a millisecond timestamp) -> `"...<PHONE> ms total"`

  This has not been narrowed, because doing so is a security-relevant
  precision/recall trade-off that should be made with real evidence from
  actual test documents, not guessed at. If this turns out to be too
  aggressive for a given document set (e.g. consumer-app screenshots full of
  video IDs, order numbers, timestamps), that's a product decision for
  the Architect/team, not something this tool should quietly loosen on its
  own.
- **Person names are masked with a shape heuristic, not a real name
  detector**: any two-or-three consecutive Capitalized Words are replaced
  with `<NAME>` (`patterns.py`'s `mask_person_names`). Unlike SSN/email/
  phone, a name has no fixed format to match. A stoplist of common English/
  UI words (`_COMMON_NON_NAME_WORDS`) keeps ordinary nav chrome ("Sign In",
  "Search Images", "Show more") from being masked, but it **cannot** tell a
  real person's name apart from any other two-word proper noun that isn't
  common UI vocabulary -- a video title, song title, or band name (e.g.
  "Severus Snape", "Tom Odell") is masked exactly the same as a real name,
  by design: the tool has no way to know which is which. A sentence-initial
  word immediately followed by a stoplisted UI label can also still false-
  positive (e.g. "Clicked Sign In"), since sentence-initial capitalization
  looks identical to a name's first word. A proper NER model (e.g. spaCy)
  would handle both cases more precisely but is a heavier dependency; see
  this project's decision log for why V1 shipped the regex heuristic
  instead.
- **All evidence for a document is sent to the LLM in a single prompt**, with
  no chunking. A document with a very large number of screenshots could
  approach the model's context window; V1 has no truncation or batching
  strategy for that case.

## Running tests

From the qa-ai-copilot repo root:

```
python -m pytest secure_test_step_generator/tests -v
```
