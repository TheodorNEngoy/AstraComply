import pytest
from pydantic import BaseModel
import yaml
import sys
sys.path.append('.')
from streamlit_app import assess, Answer

rulebook = yaml.safe_load(open("templates/risk_assessment.yml"))

def make_answer(qid, val): return Answer(question_id=qid, answer=val)

@ pytest.mark.parametrize("answers,expected", [
    ([make_answer('q1','no')], 'minimal'),
    ([make_answer('q1','yes')], 'high-risk'),
    ([make_answer('q2','yes'), make_answer('q3','no')], 'high-risk'),
])
def test_assess(answers, expected):
    assert assess(answers) == expected