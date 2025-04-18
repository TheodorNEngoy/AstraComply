from fastapi import FastAPI
from pydantic import BaseModel
import yaml
from jinja2 import Environment, FileSystemLoader

# --- Data models --------------------------------
class Answer(BaseModel):
    question_id: str
    answer: str

class AssessRequest(BaseModel):
    answers: list[Answer]

class AssessResponse(BaseModel):
    risk_tier: str

# --- App setup ---------------------------------
app = FastAPI(title="AstraComply API")
rulebook = yaml.safe_load(open("templates/risk_assessment.yml", "r"))
env = Environment(loader=FileSystemLoader("templates"))

# --- Endpoints ---------------------------------
@app.post("/assess", response_model=AssessResponse)
def assess(payload: AssessRequest):
    """
    Simple rule‑engine: if any answer matches a high_risk_value, mark high‑risk.
    """
    risk = "minimal"
    for ans in payload.answers:
        rules = rulebook.get(ans.question_id, {})
        hr_vals = rules.get("high_risk_values", [])
        if ans.answer.lower() in [v.lower() for v in hr_vals]:
            risk = "high‑risk"
            break
    return AssessResponse(risk_tier=risk)

@app.post("/generate")
def generate_report(payload: AssessRequest):
    """
    Render the Markdown report via Jinja2 and return it.
    """
    # reuse assess logic
    assessed = assess(payload)
    template = env.get_template("report.tpl.md")
    document = template.render(
        risk_tier=assessed.risk_tier,
        answers=[a.dict() for a in payload.answers]
    )
    return {"document": document}
