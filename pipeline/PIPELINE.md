# 주식투자 AI 에이전트 파이프라인

매일 1회 실행되는 8단계(가상 직원 8명) 파이프라인입니다. 이 문서는 Cron으로
깨어난 Claude Code 세션이 그대로 따라야 하는 작업 지시서입니다. 각 단계는
JSON 산출물을 `reports/<YYYY-MM-DD>/` 아래에 저장하고, 다음 단계는 이전
단계의 JSON을 입력으로 사용합니다.

사용 가능한 도구:
- `mcp__PlayMCP__NaverSearch-search_news` 등 : 뉴스/공시 검색
- `mcp__FMP__*` : 미국 시장 재무/공시/수급 데이터
- 한국 시장 데이터는 뉴스 검색 결과와 공개된 공시 정보로 보강 (전용 API 미연결)
- `mcp__Gmail__create_draft` : 최종 보고서 메일 초안 생성

실행 순서:

## 0. 준비
- 오늘 날짜로 `reports/<date>/` 디렉터리를 만든다.

## 1단계 — 뉴스 스카우트 (2명, 역할 분담: 국내 / 해외)
- 직원 A(국내): NaverSearch로 최근 24시간 국내 경제/증시 뉴스를 검색해
  주목할 만한 기업·산업 트렌드를 5~10개 후보로 추출.
- 직원 B(해외): FMP 또는 뉴스 검색으로 미국/글로벌 시장 트렌드와 관련 기업
  후보를 5~10개 추출.
- 두 명의 결과를 합쳐 중복 제거 후 `01_news_candidates.json` 저장.
  스키마: `[{ "ticker": str|null, "name": str, "market": "KR"|"US",
  "reason": str, "source_urls": [str] }]`

## 2단계 — 동종업계 비교 분석가 (2명)
- 1단계 후보 중 같은 산업군으로 묶을 수 있는 3개 기업(업계 1위~3위 포함)
  세트를 선정.
- 직원 C: 각 기업의 시장 지위, 점유율, 경쟁 우위를 뉴스/검색으로 조사.
- 직원 D: 동일 세트에 대해 투자자 관점(밸류에이션, 성장성 비교)으로 교차
  검증하고 어느 기업이 우량한지 1차 의견을 낸다.
- `02_peer_comparison.json` 저장.
  스키마: `[{ "industry": str, "companies": [{ "ticker": str, "name": str,
  "rank_in_industry": int }], "analysis": str, "leading_candidate": str }]`

## 3단계 — 기업 세부정보 분석가 (2명)
- 2단계에서 유력 후보로 압축된 기업들에 대해:
  - 기초정보(설립, 사업영역), 재무상태(재무제표 핵심 지표), 기업공시(최근
    공시), 매출정보, 과거 3년 매출 추이, 배당정보를 조사.
  - 직원 E: 재무/공시/매출 담당. 직원 F: 배당/사업개요 담당.
- `03_fundamentals.json` 저장.
  스키마: `[{ "ticker": str, "name": str, "overview": str,
  "financials": {...}, "disclosures": [str], "revenue_3y": [number,
  number, number], "dividend": {...} }]`

## 4단계 — 수급 분석가 (1명)
- 선정 기업들의 외국인/기관/개인 수급 현황(가능한 데이터 범위 내)을
  조사하여 거래가 원활한지(유동성, 수급 쏠림) 판단.
- `04_flow.json` 저장.
  스키마: `[{ "ticker": str, "foreign_flow": str, "institution_flow": str,
  "retail_flow": str, "liquidity_judgement": str }]`

## 5단계 — 최종 결정자 (1명)
- 1~4단계 산출물을 모두 검토하여 회의 형식으로 종합 토론 요약을 작성하고
  최종 투자 후보 1~3개를 선정, 근거를 명시.
- `05_decision.json` 저장.
  스키마: `{ "meeting_summary": str, "selected_companies": [{ "ticker": str,
  "name": str, "rationale": str }], "date": "YYYY-MM-DD" }`

## 6단계 — 보고서 생성 및 발송
- `python3 pipeline/generate_pdf.py reports/<date>` 실행 → 같은 폴더에
  `report.pdf` 생성.
- `mcp__Gmail__create_draft` 로 받는사람 dohamsushin@gmail.com, 제목
  "[주식 AI 에이전트] <date> 투자 후보 보고서", 본문에 핵심 요약, PDF 첨부.
  (Gmail MCP는 발송 기능이 없어 초안만 생성됨 — 사용자가 직접 확인 후 전송)
