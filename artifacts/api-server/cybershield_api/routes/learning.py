from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_user
from ..learning import LESSONS, get_lesson, public_lesson, public_lesson_summary
from ..models import LearningProgressRecord, User, utcnow
from ..schemas import LearningProgress, Lesson, LessonDetail, QuizResult, QuizSubmission

router = APIRouter(prefix="/api/learning", tags=["learning"])
PASS_SCORE = 70


def _progress_map(user_id: int, db: Session) -> dict[str, dict]:
    records = db.scalars(
        select(LearningProgressRecord).where(LearningProgressRecord.user_id == user_id)
    ).all()
    return {
        record.lesson_slug: {
            "completed": record.completed,
            "best_score": record.best_score,
        }
        for record in records
    }


@router.get("/modules", response_model=list[Lesson])
def list_lessons(user: User = Depends(require_user), db: Session = Depends(get_db)):
    progress = _progress_map(user.id, db)
    return [public_lesson_summary(lesson, progress.get(lesson["slug"])) for lesson in LESSONS]


@router.get("/modules/{slug}", response_model=LessonDetail)
def get_lesson_detail(
    slug: str,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    lesson = get_lesson(slug)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Learning module not found.")
    return public_lesson(lesson, _progress_map(user.id, db).get(slug))


@router.post("/modules/{slug}/quiz", response_model=QuizResult)
def submit_quiz(
    slug: str,
    payload: QuizSubmission,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    lesson = get_lesson(slug)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Learning module not found.")
    submitted = {answer.question_id: answer.selected_option for answer in payload.answers}
    questions = lesson["questions"]
    expected_ids = {question["id"] for question in questions}
    if len(submitted) != len(payload.answers) or set(submitted) != expected_ids:
        raise HTTPException(status_code=400, detail="Submit one answer for each quiz question.")

    feedback = []
    correct_answers = 0
    for question in questions:
        selected = submitted[question["id"]]
        correct_option = question["correct"]
        is_correct = selected == correct_option
        correct_answers += int(is_correct)
        feedback.append(
            {
                "question_id": question["id"],
                "correct": is_correct,
                "correct_option": correct_option,
                "explanation": question["explanation"],
            }
        )
    score = round(correct_answers * 100 / len(questions))
    passed = score >= PASS_SCORE
    record = db.scalar(
        select(LearningProgressRecord).where(
            LearningProgressRecord.user_id == user.id,
            LearningProgressRecord.lesson_slug == slug,
        )
    )
    if record is None:
        record = LearningProgressRecord(
            user_id=user.id,
            lesson_slug=slug,
            best_score=score,
            completed=passed,
            completed_at=utcnow() if passed else None,
        )
        db.add(record)
    else:
        record.best_score = max(record.best_score, score)
        if passed and not record.completed:
            record.completed = True
            record.completed_at = utcnow()
        record.updated_at = utcnow()
    db.commit()
    return QuizResult(
        score=score,
        correct_answers=correct_answers,
        total_questions=len(questions),
        passed=passed,
        feedback=feedback,
    )


@router.get("/progress", response_model=LearningProgress)
def get_learning_progress(
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    records = db.scalars(
        select(LearningProgressRecord).where(LearningProgressRecord.user_id == user.id)
    ).all()
    scores = [record.best_score for record in records]
    return LearningProgress(
        completed_lessons=sum(record.completed for record in records),
        total_lessons=len(LESSONS),
        average_score=round(sum(scores) / len(scores), 1) if scores else None,
    )
