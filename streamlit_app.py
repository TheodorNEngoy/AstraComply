import streamlit as st
from pydantic import BaseModel
import yaml
from jinja2 import Environment, FileSystemLoader

# --- Load rulebook & templates ----------------
rulebook = yaml.safe_load(open("templates/risk_assessment.yml"))
env = Environment(loader=FileSystemLoader("templates"))

# --- Pydantic model for validation ----------
class Answer(BaseModel):
    question_id: str
    answer: str

# --- Helper functions -------------------------
def assess(answers: list[Answer]) -> str:
    for ans in answers:
        rules = rulebook.get(ans.question_id, {})
        if ans.answer.lower() in [v.lower() for v in rules.get("high_risk_values", [])]:
            return "high‑risk"
    return "minimal"

def render_report(risk_tier: str, answers: list[Answer]) -> str:
    tpl = env.get_template("report.tpl.md")
    return tpl.render(risk_tier=risk_tier, answers=[a.dict() for a in answers])

# --- Streamlit UI ----------------------------
st.title("AstraComply – EU AI Act Self‑Assessment")

# Load questions from the rulebook
answers = []
for qid, meta in rulebook.items():
    ans = st.selectbox(meta["text"], ["yes", "no"], key=qid)
    answers.append(Answer(question_id=qid, answer=ans))

if st.button("Assess risk tier"):
    tier = assess(answers)
    st.markdown(f"## 🔍 Risk tier: **{tier}**")

if st.button("Generate report"):
    tier = assess(answers)
    md = render_report(tier, answers)
    st.download_button(
        "Download Markdown report",
        data=md,
        file_name="astra_report.md",
        mime="text/markdown"
    )
    st.markdown("### Preview")
    st.markdown(md)