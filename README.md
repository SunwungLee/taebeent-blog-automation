# Blogspot Agent System (Python Automation)

이 프로젝트는 구글 시트를 데이터베이스로 사용하고, Gemini/OpenAI 및 Blogger API를 연동하여 Blogspot 포스팅 전 과정을 자동화하는 상태 기반(State-driven) 시스템입니다.

## 🛠️ 주요 기능

1.  **State-driven Workflow**: 키워드 수집부터 발행까지 리액티브한 상태 관리를 지원합니다.
2.  **HTML Generation & Validation**: SEO에 최적화된 HTML 구조(H2, P, FAQ)를 생성하고 자동 검증합니다.
3.  **Multi-LLM Support**: Gemini 2.0 Flash를 기본으로 사용하며, 할당량 초과 시 OpenAI(GPT-4o)로 자동 폴백합니다.
4.  **Google Sheets Integration**: 모든 데이터와 상태를 구글 시트에서 한눈에 관리합니다.
5.  **GitHub Actions Compatible**: CLI 기반 인터페이스로 로컬 및 클라우드 환경에서 쉽게 실행 가능합니다.

## 🚀 시작하기

### 1. 필수 패키지 설치
터미널에서 아래 명령어를 실행하여 필요한 라이브러리를 설치하세요.
```bash
python -m pip install -r requirements.txt
```

### 2. API 설정 (.env 파일 작성)
현재 폴더의 `.env` 파일에 아래 정보들을 채워주세요.
- **GEMINI_API_KEY**: Google AI Studio에서 발급받은 키
- **OPENAI_API_KEY**: OpenAI API 키 (Fallback용)
- **GOOGLE_SHEET_ID**: 관리용 구글 시트의 ID
- **BLOGGER_CLIENT_ID / SECRET**: Google Cloud OAuth 2.0 클라이언트 정보
- **BLOGGER_BLOG_ID**: Blogspot 블로그 ID

### 3. 인증 파일 준비
- **credentials/service_account.json**: 구글 시트 API용 서비스 계정 키 파일

## 📂 폴더 구조 및 모듈
- `app/main.py`: CLI 엔트리포인트
- `app/sheets_client.py`: 구글 시트 연동 클라이언트
- `app/blogger_client.py`: Blogger API 연동 클라이언트
- `app/generator/`: 콘텐츠 생성 및 검증 로직 (Prompt, HTML, Validator)
- `app/services/`: 비즈니스 로직 레이어 (Keyword, Post, Publish Service)
- `app/state_machine.py`: 상태 전이 관리 로직
- `app/models.py`: 데이터 모델 정의

## 🚀 실행 방법 (CLI)

모든 명령은 프로젝트 루트 디렉토리에서 실행합니다.

### 1. 콘텐츠 생성
시트에서 `approved_for_writing` 상태인 키워드를 읽어 HTML을 생성하고 `posts` 시트에 저장합니다.
```bash
python -m app.main generate --limit 3
```

### 2. 블로그 발행
`ready_to_publish` 상태인 포스트를 실제 Blogspot 블로그에 게시합니다.
```bash
python -m app.main publish --limit 2
```

## 🤖 자동화 팁
GitHub Actions를 사용하여 스케줄(Cron) 기반으로 자동화를 구성하는 것을 추천합니다.
`python -m app.main generate`와 `python -m app.main publish` 명령어를 워크플로우에 추가하여 완전 자동화를 구현할 수 있습니다.
