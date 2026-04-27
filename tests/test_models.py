import pytest
from pydantic import ValidationError
from src.stresstestercli.models import parse_llm_json

def test_parse_llm_json_malformed():
    malformed = '{"verdict": "pass", "score": 100, "issues": ["ok"], "suggestions": "none"'  # missing closing }
    with pytest.raises(ValidationError):
        parse_llm_json(malformed)

def test_parse_llm_json_fail_empty_issues():
    bad_json = '{"verdict": "fail", "score": 50, "issues": [], "suggestions": "fix it"}'
    with pytest.raises(ValidationError):
        parse_llm_json(bad_json)