from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator


def to_camel(value: str) -> str:
    first, *rest = value.split("_")
    return first + "".join(part.capitalize() for part in rest)


class ApiModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class ApiError(ApiModel):
    detail: str


class HealthStatus(ApiModel):
    status: str


class SuccessMessage(ApiModel):
    message: str


class UserRead(ApiModel):
    id: int
    email: EmailStr
    display_name: str
    created_at: datetime


class SessionState(ApiModel):
    authenticated: bool
    user: UserRead | None


class RegisterInput(ApiModel):
    email: EmailStr
    display_name: str = Field(min_length=1, max_length=80)
    password: SecretStr = Field(min_length=12, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().casefold()

    @field_validator("display_name")
    @classmethod
    def normalize_display_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Display name cannot be blank.")
        return normalized


class LoginInput(ApiModel):
    email: EmailStr
    password: SecretStr = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().casefold()


class RiskCategory(str):
    pass


class Finding(ApiModel):
    code: str
    title: str
    description: str
    points: int
    severity: Literal["info", "low", "medium", "high"]


class AnalysisInput(ApiModel):
    url: str = Field(min_length=1, max_length=2048)


class Analysis(ApiModel):
    id: int
    url: str
    normalized_url: str
    score: int = Field(ge=0, le=100)
    category: Literal["Low", "Medium", "High", "Critical"]
    findings: list[Finding]
    recommendation: str
    created_at: datetime


class RiskCount(ApiModel):
    category: Literal["Low", "Medium", "High", "Critical"]
    count: int


class DailyCount(ApiModel):
    date: date
    count: int


class DashboardSummary(ApiModel):
    total_analyses: int
    distribution: list[RiskCount]
    trend: list[DailyCount]
    recent_analyses: list[Analysis]
    high_risk_count: int


class Lesson(ApiModel):
    slug: str
    title: str
    topic: str
    summary: str
    minutes: int
    completed: bool
    best_score: int | None


class QuizOption(ApiModel):
    label: str
    text: str


class QuizQuestion(ApiModel):
    id: str
    prompt: str
    options: list[QuizOption]


class LessonSection(ApiModel):
    heading: str
    body: str
    key_takeaway: str


class LessonDetail(ApiModel):
    slug: str
    title: str
    topic: str
    summary: str
    minutes: int
    sections: list[LessonSection]
    questions: list[QuizQuestion]
    completed: bool
    best_score: int | None


class QuizAnswer(ApiModel):
    question_id: str = Field(min_length=1, max_length=80)
    selected_option: int = Field(ge=0, le=5)


class QuizSubmission(ApiModel):
    answers: list[QuizAnswer] = Field(min_length=1, max_length=20)


class QuizFeedback(ApiModel):
    question_id: str
    correct: bool
    correct_option: int
    explanation: str


class QuizResult(ApiModel):
    score: int = Field(ge=0, le=100)
    correct_answers: int
    total_questions: int
    passed: bool
    feedback: list[QuizFeedback]


class LearningProgress(ApiModel):
    completed_lessons: int
    total_lessons: int
    average_score: float | None


class Settings(ApiModel):
    email: EmailStr
    display_name: str
    created_at: datetime


class SettingsUpdate(ApiModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=80)

    @field_validator("display_name")
    @classmethod
    def normalize_display_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("Display name cannot be blank.")
        return normalized
