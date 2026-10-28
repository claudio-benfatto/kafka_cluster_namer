import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Finding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    file: str = Field(description="Path of the file, relative to the repo root")
    line: int = Field(description="Line number in the NEW version of the file")
    severity: Literal["critical", "major", "minor"]
    message: str


class Review(BaseModel):
    model_config = ConfigDict(extra="forbid")

    findings: list[Finding]


if __name__ == "__main__":
    print(json.dumps(Review.model_json_schema()))
