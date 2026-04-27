from pydantic import BaseModel, Field, field_validator
from typing import Literal

class CodeReview(BaseModel):
    verdict: Literal["pass", "warn", "fail"]
    score: int = Field(..., ge=0, le=100)
    issues: list[str]
    suggestions: str
    
    @field_validator("issues")
    @classmethod
    def issues_not_empty_on_fail(cls, v, info):
        if info.data.get("verdict") == "fail" and not v:
            raise ValueError("fail verdict must have issues")
        return v

def parse_llm_json(raw: str) -> CodeReview:
    """
    Strips markdown code fences from a string and parses it as a CodeReview object.
    """
    import re
    # Remove markdown code fences (``` or ```json)
    cleaned = re.sub(r"^```(?:json)?\\s*|\\s*```$", "", raw.strip(), flags=re.IGNORECASE | re.MULTILINE)
    return CodeReview.model_validate_json(cleaned)