# Blog Automation System — Multi-Agent Edition

구글 뉴스, 구글 시트, OpenAI API, Blogger를 연동하여
블로그 포스팅 전 과정을 **6개의 독립 에이전트**로 자동화하는 시스템입니다.

---

## 🤖 에이전트 구조

```
Orchestrator (메인 Supervisor)
├── 1. KeywordSeekerAgent    — 구글 뉴스 RSS로 트렌딩 키워드 발굴
├── 2. KeywordAnalyzerAgent  — GPT 기반 키워드 우선순위 분석
├── 3. ContentsCreatorAgent  — 초안 작성 + 편집/SEO 최적화
├── 4. PublisherAgent        — Blogger API로 포스트 발행
└── 5. BlogAnalyzerAgent     — 발행 포스트 성과 분석 및 인사이트 제안
```

### 상태 흐름

```
PENDING → (KeywordAnalyzer) → SKIPPED
                            ↓ (통과)
                         PENDING → DRAFTED → APPROVED → PUBLISHED
                         (Writer)  (Editor)   (Publisher)
```

---

## 🛠️ 주요 기능

| 에이전트 | 역할 |
|---|---|
| **KeywordSeeker** | 구글 뉴스(KR) RSS 크롤링 → 신규 토픽을 Sheets에 `PENDING`으로 저장 |
| **KeywordAnalyzer** | `gpt-4o-mini`로 토픽의 블로그 가치 점수화, 낮은 우선순위는 `SKIPPED` 처리 |
| **ContentsCreator** | `PENDING` → 초안 작성(`DRAFTED`) → 편집·SEO 최적화(`APPROVED`) |
| **Publisher** | `APPROVED` 콘텐츠를 Markdown → HTML 변환 후 Blogger에 게시 |
| **BlogAnalyzer** | 발행된 포스트 통계 수집 + GPT 기반 콘텐츠 개선 인사이트 제안 |

---

## 🚀 시작하기

### 1. 필수 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. `.env` 파일 작성

프로젝트 루트에 `.env` 파일을 생성하고 아래 값을 채워주세요.

```env
OPENAI_API_KEY=sk-...
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_SERVICE_ACCOUNT_JSON=credentials/service_account.json
BLOGGER_CLIENT_ID=your_client_id
BLOGGER_CLIENT_SECRET=your_client_secret
BLOGGER_BLOG_ID=your_blog_id
```

### 3. 인증 파일 준비

`credentials/` 폴더에 아래 파일을 준비하세요.

- **`service_account.json`**: Google Sheets API용 서비스 계정 키
  - 해당 이메일로 관리용 구글 시트를 공유(편집자 권한)

---

## 📂 폴더 구조

```
├── main.py                        # 진입점 (Orchestrator 실행)
├── requirements.txt
├── .env                           # API 키 (git 제외)
├── credentials/
│   ├── service_account.json       # Sheets 서비스 계정 키
│   └── token.json                 # Blogger OAuth 토큰 (자동 생성)
└── src/
    ├── config.py                  # 환경변수 로더
    ├── agents/                    # ✨ 멀티 에이전트
    │   ├── base_agent.py          # 공통 BaseAgent
    │   ├── orchestrator.py        # 파이프라인 총괄
    │   ├── keyword_seeker.py      # 키워드 탐색
    │   ├── keyword_analyzer.py    # 키워드 분석
    │   ├── contents_creator.py    # 콘텐츠 생성·편집
    │   ├── publisher.py           # Blogger 발행
    │   └── blog_analyzer.py       # 성과 분석
    ├── core/                      # 레거시 모듈 (참조용)
    └── integrations/
        └── google_sheets.py       # Sheets CRUD
```

---

## ▶️ 실행 방법

### 전체 파이프라인 실행

```bash
python main.py
```

### 에이전트 개별 실행 (테스트용)

```bash
python -m src.agents.keyword_seeker
python -m src.agents.keyword_analyzer
python -m src.agents.contents_creator
python -m src.agents.publisher
python -m src.agents.blog_analyzer
```

---

## ⚙️ Orchestrator 설정

`main.py`에서 아래 파라미터로 동작을 조정할 수 있습니다.

```python
orchestrator = Orchestrator(
    region="KR",           # 구글 뉴스 지역 코드
    keyword_limit=5,       # 1회 실행당 최대 탐색 키워드 수
    min_keyword_score=5,   # 콘텐츠 생성 최소 점수 (1~10)
    post_limit=10,         # 성과 분석할 최근 포스트 수
)
```

---

## 🤖 자동화 팁

| 방법 | 설명 |
|---|---|
| **Windows 작업 스케줄러** | 로컬 PC에서 특정 시간마다 자동 실행 |
| **GitHub Actions** | 무료 클라우드 스케줄 실행 (추천) |
| **Cloud VPS** | 서버 임대 후 24시간 상시 실행 |
