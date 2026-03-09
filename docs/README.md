# proposal-gen

Turns Granola meeting notes into a branded Cloudtech proposal PDF — in seconds.

## How it works

1. SDR pastes Granola notes into the web form
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

# 3. Run
python app.py
# → http://localhost:5000
```

## Deploy to Railway

```bash
npm install -g @railway/cli
railway login
railway init   # name it proposal-gen
railway up
railway variables set ANTHROPIC_API_KEY=sk-ant-...
```

## Environment Variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API key |
| `PORT` | Server port (default: 5000) |

## Status
🚧 Work in progress
