# proposal-gen

Turns meeting  notes into a branded Cloudtech proposal PDF — in seconds.

## How it works

1. SDR pastes meeting notes into the web form
2. Claude reads the notes and generates structured proposal content
3. Tool renders branded HTML (real header/footer images embedded)
4. Converts to PDF via WeasyPrint — no Google API, no external services
5. Form returns a PDF download instantly

**Pricing is left blank** — founder opens the PDF, or re-runs with cost filled in.

## Stack

- Python / Flask backend
- Claude Sonnet for proposal generation
- WeasyPrint for HTML → PDF conversion
- Vanilla HTML/JS frontend (no build step)
- Header/footer images stored in `static/`

## Setup

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Add your ANTHROPIC_API_KEY
# add port number

# 3. Run
python app.py
# → http://localhost:<port>
```


```

## Environment Variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API key |
| `PORT` | Server port |

## Status
🚧 Work in progress
