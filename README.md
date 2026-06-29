# dohamsu

## 주식투자 AI 에이전트 파이프라인

매일 실행되는 8단계(뉴스 스카우트 2명 → 동종업계 비교 2명 → 기업 세부분석 2명
→ 수급 분석 1명 → 최종 결정 1명) 멀티에이전트 주식 분석 파이프라인입니다.

- 작업 지시서: [`pipeline/PIPELINE.md`](pipeline/PIPELINE.md)
- PDF 보고서 생성: `python3 pipeline/generate_pdf.py reports/<date>`
- Cron으로 매일 Claude Code 세션이 깨어나 `PIPELINE.md`의 단계를 수행하고,
  `reports/<date>/`에 JSON 산출물과 `report.pdf`를 남기고, Gmail에 보고서
  메일 초안을 생성합니다.
