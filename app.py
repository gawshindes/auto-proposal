import os
import json
from dotenv import load_dotenv
load_dotenv()
import re
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import base64

app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
BASE_DIR = Path(__file__).parent


def load_prompt():
    return (BASE_DIR / "prompts" / "proposal.md").read_text()


def img_to_base64(path):
    suffix = path.suffix.lower()
    mime = "image/jpeg" if suffix in (".jpg", ".jpeg") else "image/png"
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:{mime};base64,{data}"


def call_claude(meeting_notes, extra_context):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    user_msg = f"Meeting notes:\n\n{meeting_notes}"
    if extra_context.strip():
        user_msg += f"\n\nAdditional context:\n{extra_context}"
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=load_prompt(),
        messages=[{"role": "user", "content": user_msg}],
    )
    raw = msg.content[0].text.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


def render_proposal_html(proposal):
    header_b64 = img_to_base64(BASE_DIR / "static" / "header.png")
    footer_b64 = img_to_base64(BASE_DIR / "static" / "footer.jpeg")

    weeks_html = ""
    for week in proposal["weeks"]:
        goals_li = "".join(f"<li>{g}</li>" for g in week["goals"])
        acts_li  = "".join(f"<li>{a}</li>" for a in week["activities"])
        weeks_html += f"""
        <div class="week">
          <h3>{week['title']}</h3>
          <p class="section-label">Goals:</p>
          <ul>{goals_li}</ul>
          <p class="section-label">Key Activities:</p>
          <ul>{acts_li}</ul>
        </div>"""

    assumptions_li = "".join(f"<li>{a}</li>" for a in proposal["assumptions"])
    constraints_li = "".join(f"<li>{c}</li>" for c in proposal["constraints"])
    cost = proposal.get("summary_cost", "[TBD — Founder to complete]")

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"/>
<style>
  @page {{ size: A4; margin: 0; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: Helvetica, Arial, sans-serif; font-size: 10.5pt; color: #1f2937; background: white; }}
  .page {{ width: 210mm; min-height: 297mm; display: flex; flex-direction: column; }}
  .header img, .footer img {{ width: 100%; display: block; }}
  .body {{ flex: 1; padding: 14mm 18mm 8mm 18mm; }}
  .doc-title {{ font-size: 15pt; font-weight: 700; color: #111827; text-align: center; margin-bottom: 5mm; }}
  .summary {{ border: 1.5px solid #e5e7eb; border-radius: 6px; padding: 4mm 6mm; margin-bottom: 6mm; background: #f9fafb; }}
  .summary h2 {{ font-size: 11pt; font-weight: 700; border-bottom: 1.5px solid #e5e7eb; padding-bottom: 2mm; margin-bottom: 3mm; text-decoration: underline; text-underline-offset: 3px; }}
  .summary-row {{ display: flex; gap: 2mm; margin-bottom: 1.5mm; font-size: 10pt; }}
  .summary-row .lbl {{ font-weight: 700; min-width: 20mm; }}
  .cost {{ color: #b45309; font-style: italic; }}
  h2.section {{ font-size: 12pt; font-weight: 700; border-bottom: 1.5px solid #e5e7eb; padding-bottom: 2mm; margin-bottom: 4mm; text-decoration: underline; text-underline-offset: 3px; }}
  .week {{ margin-bottom: 6mm; page-break-inside: avoid; }}
  .week h3 {{ font-size: 11pt; font-weight: 700; color: #2563eb; margin-bottom: 2mm; }}
  .section-label {{ font-size: 9pt; font-weight: 700; color: #6b7280; margin-top: 2mm; margin-bottom: 1mm; text-transform: uppercase; letter-spacing: 0.04em; }}
  ul {{ padding-left: 5mm; }}
  li {{ font-size: 10pt; color: #374151; margin-bottom: 1mm; line-height: 1.4; list-style-type: disc; }}
  .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6mm; margin-top: 5mm; page-break-inside: avoid; }}
  .footer {{ margin-top: auto; }}
</style>
</head>
<body>
<div class="page">
  <div class="header"><img src="{header_b64}" /></div>
  <div class="body">
    <div class="doc-title">Proposal and Scope of Work — {proposal['customer_name']}</div>
    <div class="summary">
      <h2>Summary</h2>
      <div class="summary-row"><span class="lbl">Scope:</span><span>{proposal['summary_scope']}</span></div>
      <div class="summary-row"><span class="lbl">Timeline:</span><span>{proposal['summary_timeline']}</span></div>
      <div class="summary-row"><span class="lbl">Cost:</span><span class="cost">{cost}</span></div>
    </div>
    <h2 class="section">Detailed Scope of Work</h2>
    {weeks_html}
    <div class="two-col">
      <div><h2 class="section">Assumptions</h2><ul>{assumptions_li}</ul></div>
      <div><h2 class="section">Constraints</h2><ul>{constraints_li}</ul></div>
    </div>
  </div>
  <div class="footer"><img src="{footer_b64}" /></div>
</div>
</body></html>"""



@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json or {}
    meeting_notes = data.get("meeting_notes", "").strip()
    extra_context = data.get("extra_context", "").strip()
    if not meeting_notes:
        return jsonify({"error": "meeting_notes is required"}), 400
    try:
        proposal  = call_claude(meeting_notes, extra_context)
        html      = render_proposal_html(proposal)
        return jsonify({
            "success":       True,
            "customer_name": proposal["customer_name"],
            "html_base64":   base64.b64encode(html.encode()).decode(),
            "summary": {
                "scope":    proposal["summary_scope"],
                "timeline": proposal["summary_timeline"],
                "weeks":    len(proposal["weeks"]),
            }
        })
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Claude returned invalid JSON: {e}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
