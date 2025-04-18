import streamlit as st
from pydantic import BaseModel
import yaml
from jinja2 import Environment, FileSystemLoader
import datetime
import pdfkit
from docx import Document
import io
import os

# --- Load config & templates ----------------
config = yaml.safe_load(open("config.yaml"))
rulebook = yaml.safe_load(open("templates/risk_assessment.yml"))
env = Environment(loader=FileSystemLoader("templates"))

# --- Streamlit page setup & logo -------------
st.set_page_config(page_title=config['company_name'], page_icon=config.get('logo_path', None))
logo_path = config.get('logo_path', '')
if logo_path and os.path.exists(logo_path):
    st.image(logo_path, width=120)
else:
    st.header(config['company_name'])

st.title(f"{config['company_name']} – EU AI Act Self‑Assessment")

# --- Pydantic model -------------------------
class Answer(BaseModel):
    question_id: str
    answer: str

# --- Helper functions -----------------------
def assess(answers: list[Answer]) -> str:
    for ans in answers:
        rules = rulebook.get(ans.question_id, {})
        if ans.answer.lower() in [v.lower() for v in rules.get("high_risk_values", [])]:
            return "high-risk"
    return "minimal"

def render_report_md(risk_tier: str, answers: list[Answer], timestamp: str) -> str:
    tpl = env.get_template("report.tpl.md")
    return tpl.render(risk_tier=risk_tier, answers=[a.dict() for a in answers], timestamp=timestamp)

def render_report_docx(md: str) -> bytes:
    doc = Document()
    for line in md.split("\n"):
        doc.add_paragraph(line)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()

def render_report_pdf(md: str) -> bytes:
    # converts Markdown -> HTML -> PDF via pdfkit
    html = md.replace("\n", "<br />")
    return pdfkit.from_string(html, False)

# --- Streamlit UI ----------------------------
# collect answers
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
answers = []
for qid, meta in rulebook.items():
    ans = st.selectbox(meta["text"], meta.get("options", ["yes", "no"]), key=qid)
    answers.append(Answer(question_id=qid, answer=ans))

if st.button("Assess risk tier"):
    tier = assess(answers)
    st.markdown(f"## 🔍 Risk tier: **{tier}**")

if st.button("Generate report"):
    tier = assess(answers)
    md = render_report_md(tier, answers, timestamp)

    # Markdown download
    st.download_button(
        "Download Markdown report",
        data=md,
        file_name="astra_report.md",
        mime="text/markdown"
    )

    # DOCX download
    docx_bytes = render_report_docx(md)
    st.download_button(
        "Download DOCX report",
        data=docx_bytes,
        file_name="astra_report.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # PDF download (requires wkhtmltopdf)
    try:
        pdf_bytes = render_report_pdf(md)
        st.download_button(
            "Download PDF report",
            data=pdf_bytes,
            file_name="astra_report.pdf",
            mime="application/pdf"
        )
    except Exception:
        st.warning("PDF export requires wkhtmltopdf installed in your environment.")

    # Preview the Markdown
    st.markdown("### Preview")
    st.markdown(md)
