#!/usr/bin/env python3
"""Render the 5-stage JSON pipeline output into reports/<date>/report.pdf.

Usage: python3 generate_pdf.py reports/<date>
Expects 01_news_candidates.json .. 05_decision.json in that directory.
"""
import json
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem,
)


def load(dir_path: Path, name: str):
    f = dir_path / name
    if not f.exists():
        return None
    return json.loads(f.read_text(encoding="utf-8"))


def build(dir_path: Path):
    news = load(dir_path, "01_news_candidates.json") or []
    peers = load(dir_path, "02_peer_comparison.json") or []
    fundamentals = load(dir_path, "03_fundamentals.json") or []
    flow = load(dir_path, "04_flow.json") or []
    decision = load(dir_path, "05_decision.json") or {}

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], spaceAfter=8)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], spaceAfter=6)
    body = styles["BodyText"]

    story = []
    date = decision.get("date", dir_path.name)
    story.append(Paragraph(f"주식투자 AI 에이전트 보고서 — {date}", h1))
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("1. 오늘의 후보 기업 (뉴스 스카우트)", h2))
    if news:
        items = [
            ListItem(Paragraph(
                f"{n.get('name')} ({n.get('ticker') or 'N/A'}, {n.get('market')}) — {n.get('reason')}",
                body))
            for n in news
        ]
        story.append(ListFlowable(items, bulletType="bullet"))
    else:
        story.append(Paragraph("데이터 없음", body))
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("2. 동종업계 비교 분석", h2))
    for p in peers:
        story.append(Paragraph(f"<b>{p.get('industry')}</b>", body))
        rows = [["순위", "기업", "티커"]] + [
            [c.get("rank_in_industry"), c.get("name"), c.get("ticker")]
            for c in p.get("companies", [])
        ]
        t = Table(rows, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ]))
        story.append(t)
        story.append(Paragraph(p.get("analysis", ""), body))
        story.append(Paragraph(f"우량 후보: {p.get('leading_candidate', '-')}", body))
        story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("3. 기업 세부정보", h2))
    for f in fundamentals:
        story.append(Paragraph(f"<b>{f.get('name')} ({f.get('ticker')})</b>", body))
        story.append(Paragraph(f.get("overview", ""), body))
        revenue = f.get("revenue_3y", [])
        story.append(Paragraph(f"과거 3년 매출: {revenue}", body))
        story.append(Paragraph(f"배당정보: {f.get('dividend', {})}", body))
        disclosures = f.get("disclosures", [])
        if disclosures:
            story.append(Paragraph("주요 공시: " + "; ".join(disclosures), body))
        story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("4. 수급 분석", h2))
    if flow:
        rows = [["티커", "외국인", "기관", "개인", "판단"]] + [
            [x.get("ticker"), x.get("foreign_flow"), x.get("institution_flow"),
             x.get("retail_flow"), x.get("liquidity_judgement")]
            for x in flow
        ]
        t = Table(rows, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("데이터 없음", body))
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("5. 최종 결정", h2))
    story.append(Paragraph(decision.get("meeting_summary", ""), body))
    for s in decision.get("selected_companies", []):
        story.append(Paragraph(f"<b>{s.get('name')} ({s.get('ticker')})</b> — {s.get('rationale')}", body))

    out = dir_path / "report.pdf"
    SimpleDocTemplate(str(out), pagesize=A4).build(story)
    print(f"wrote {out}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: generate_pdf.py <reports/date-dir>", file=sys.stderr)
        sys.exit(1)
    build(Path(sys.argv[1]))
