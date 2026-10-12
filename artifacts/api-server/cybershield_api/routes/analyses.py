from __future__ import annotations

import io
import json
from datetime import date, datetime, time, timedelta, timezone
from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_user
from ..models import AnalysisRecord, User
from ..risk import InvalidSubmittedUrl, analyze_url
from ..schemas import Analysis, AnalysisInput, DashboardSummary, DailyCount, RiskCount
from ..security import rate_limit

router = APIRouter(prefix="/api", tags=["analyses"])
RISK_CATEGORIES = ("Low", "Medium", "High", "Critical")


def _as_analysis(record: AnalysisRecord) -> Analysis:
    return Analysis(
        id=record.id,
        url=record.submitted_url,
        normalized_url=record.normalized_url,
        score=record.score,
        category=record.category,
        findings=json.loads(record.findings_json),
        recommendation=record.recommendation,
        created_at=record.created_at,
    )


@router.get("/dashboard", response_model=DashboardSummary, tags=["dashboard"])
def dashboard(user: User = Depends(require_user), db: Session = Depends(get_db)):
    records = db.scalars(
        select(AnalysisRecord)
        .where(AnalysisRecord.user_id == user.id)
        .order_by(AnalysisRecord.created_at.desc())
    ).all()
    counts = {category: 0 for category in RISK_CATEGORIES}
    today = datetime.now(timezone.utc).date()
    days = {today - timedelta(days=i): 0 for i in range(13, -1, -1)}
    high_risk_count = 0
    for record in records:
        counts[record.category] = counts.get(record.category, 0) + 1
        if record.score >= 45:
            high_risk_count += 1
        created = record.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        day = created.astimezone(timezone.utc).date()
        if day in days:
            days[day] += 1
    return DashboardSummary(
        total_analyses=len(records),
        distribution=[RiskCount(category=key, count=counts[key]) for key in RISK_CATEGORIES],
        trend=[DailyCount(date=key, count=value) for key, value in days.items()],
        recent_analyses=[_as_analysis(record) for record in records[:5]],
        high_risk_count=high_risk_count,
    )


@router.get("/analyses", response_model=list[Analysis])
def list_analyses(
    search: str | None = Query(default=None, max_length=200),
    category: str | None = Query(default=None, pattern="^(Low|Medium|High|Critical)$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    statement = select(AnalysisRecord).where(AnalysisRecord.user_id == user.id)
    if category:
        statement = statement.where(AnalysisRecord.category == category)
    records = db.scalars(
        statement.order_by(AnalysisRecord.created_at.desc()).offset(offset).limit(limit)
    ).all()
    if search:
        needle = search.casefold()
        records = [record for record in records if needle in record.submitted_url.casefold()]
    return [_as_analysis(record) for record in records]


@router.post("/analyses", response_model=Analysis, status_code=201)
def create_analysis(
    payload: AnalysisInput,
    request: Request,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    rate_limit(request, "analysis", 30, 60, subject=str(user.id))
    try:
        result = analyze_url(payload.url)
    except InvalidSubmittedUrl as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    record = AnalysisRecord(
        user_id=user.id,
        submitted_url=result["submitted_url"],
        normalized_url=result["normalized_url"],
        score=result["score"],
        category=result["category"],
        findings_json=json.dumps(result["findings"], ensure_ascii=False),
        recommendation=result["recommendation"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _as_analysis(record)


@router.get("/analyses/{analysis_id}/report", include_in_schema=True)
def download_report(
    analysis_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    record = db.scalar(
        select(AnalysisRecord).where(
            AnalysisRecord.id == analysis_id,
            AnalysisRecord.user_id == user.id,
        )
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    output = io.BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=f"CyberShield preliminary URL assessment {record.id}",
        author="CyberShield",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CyberShieldTitle",
        parent=styles["Title"],
        textColor=colors.HexColor("#10213b"),
        alignment=TA_LEFT,
        fontSize=22,
        leading=27,
        spaceAfter=8,
    )
    heading_style = ParagraphStyle(
        "CyberShieldHeading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#145b75"),
        spaceBefore=14,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "CyberShieldBody",
        parent=styles["BodyText"],
        leading=15,
        wordWrap="CJK",
        spaceAfter=6,
    )

    story = [
        Paragraph("CyberShield URL analysis", title_style),
        Paragraph(
            "<b>Automated preliminary assessment.</b> This pattern-based result is not a guarantee, "
            "a confirmation of compromise, or a professional security audit.",
            body_style,
        ),
        Spacer(1, 8),
        Paragraph("Submitted address", heading_style),
        Paragraph(escape(record.submitted_url), body_style),
        Paragraph(f"Analyzed: {escape(record.created_at.isoformat())}", body_style),
        Paragraph("Risk summary", heading_style),
    ]
    score_table = Table(
        [
            ["Risk score", f"{record.score} / 100"],
            ["Category", record.category],
        ],
        colWidths=[45 * mm, 100 * mm],
    )
    score_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#edf4f8")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#10213b")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd9e2")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("PADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(score_table)
    story.append(Paragraph("Detected indicators", heading_style))
    findings = json.loads(record.findings_json)
    if findings:
        for finding in findings:
            story.append(
                Paragraph(
                    f"<b>{escape(finding['title'])} (+{finding['points']})</b><br/>"
                    f"{escape(finding['description'])}",
                    body_style,
                )
            )
    else:
        story.append(
            Paragraph(
                "No listed warning patterns were detected. This limited check cannot verify "
                "the site or guarantee that it is safe.",
                body_style,
            )
        )
    story.extend(
        [
            Paragraph("Recommendation", heading_style),
            Paragraph(escape(record.recommendation), body_style),
            Spacer(1, 12),
            Paragraph(
                "CyberShield only parses the submitted address and does not open, crawl, or contact it. "
                "Scores reflect visible URL patterns and may miss harmful destinations or flag benign ones.",
                styles["Italic"],
            ),
        ]
    )
    document.build(story)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="cybershield-report-{record.id}.pdf"'},
    )


@router.get("/analyses/{analysis_id}", response_model=Analysis)
def get_analysis(
    analysis_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    record = db.scalar(
        select(AnalysisRecord).where(
            AnalysisRecord.id == analysis_id,
            AnalysisRecord.user_id == user.id,
        )
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return _as_analysis(record)
