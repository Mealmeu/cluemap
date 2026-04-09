from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class TestCaseInput(BaseModel):
    input_data: dict[str, Any]
    expected_output: Any
    is_hidden: bool = False
    order_index: int = 0


class TestCaseRead(ORMModel):
    id: int
    input_data: dict[str, Any]
    expected_output: Optional[Any] = None
    is_hidden: bool
    order_index: int


class ProblemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    starter_code: str = Field(min_length=1)
    reference_solution_summary: str = Field(min_length=1)
    concept_tags: list[str] = Field(default_factory=list)
    misconception_taxonomy: list[str] = Field(default_factory=list)
    test_cases: list[TestCaseInput] = Field(default_factory=list, min_length=1)


class ProblemUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    starter_code: Optional[str] = None
    reference_solution_summary: Optional[str] = None
    concept_tags: Optional[List[str]] = None
    misconception_taxonomy: Optional[List[str]] = None
    test_cases: Optional[List[TestCaseInput]] = None


class ProblemListItem(ORMModel):
    id: int
    title: str
    description: str
    concept_tags: list[str]
    created_at: datetime


class ProblemRead(ORMModel):
    id: int
    title: str
    description: str
    starter_code: str
    reference_solution_summary: str
    concept_tags: list[str]
    misconception_taxonomy: list[str]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    test_cases: list[TestCaseRead]
