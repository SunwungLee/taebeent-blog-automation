# Blog Automation System (Blogger + OpenAI)

이 프로젝트는 구글 뉴스, 구글 시트, OpenAI API 및 Blogger를 연동하여 블로그 포스팅 전 과정을 자동화하는 시스템입니다.

## 🛠️ 주요 기능

1.  **Trend Analyzer**: 구글 뉴스(South Korea) RSS를 통해 실시간 주요 뉴스를 수집하고 구글 시트에 `PENDING` 상태로 저장합니다. 
2.  **Content Writer (OpenAI)**: `gpt-4o-mini` 모델을 사용하여 시트에 저장된 주제로 전문적인 블로그 초안(Markdown)을 작성합니다.
3.  **Editor & SEO Tracker**: 작성된 초안을 다시 한번 검수하여 사실 관계 확인, 가독성 개선 및 SEO 최적화를 수행합니다.
4.  **Blogger Publisher**: 최종 승인된 글을 HTML로 변환하여 본인의 Blogger(Blogspot) 블로그에 자동으로 게시합니다.
5.  **Status Sync**: 모든 진행 상태는 구글 시트에서 한눈에 관리할 수 있습니다 (`PENDING` -> `DRAFTED` -> `APPROVED` -> `PUBLISHED`).

## 🚀 시작하기

### 1. 필수 패키지 설치
터미널(또는 CMD)에서 아래 명령어를 실행하여 필요한 라이브러리를 설치하세요.
```bash
python -m pip install -r requirements.txt
```

### 2. API 설정 (.env 파일 작성)
현재 폴더에 `.env` 파일을 생성하고 아래 정보들을 채워주세요.
- **OPENAI_API_KEY**: OpenAI API 키 (유료 크레딧 충전 필요)
- **GOOGLE_SHEET_ID**: 관리용 구글 시트의 URL에서 추출한 ID
- **BLOGGER_CLIENT_ID / SECRET**: Google Cloud Console에서 발급받은 OAuth 2.0 클라이언트 ID
- **BLOGGER_BLOG_ID**: 본인의 Blogger 블로그 ID

### 3. 인증 파일 준비
- **service_account.json**: 구글 시트 API용 서비스 계정 키 파일을 폴더에 넣고, 시트를 해당 이메일에 공유해 주세요.

## 📂 실행 방법

메인 스크립트를 실행하면 전체 프로세스가 순차적으로 진행됩니다.
```bash
python main.py
```

## 🤖 자동화 팁
컴퓨터를 직접 켜지 않고 자동화하고 싶으시다면 다음 방법들을 고려해 보세요:
1.  **Windows 작업 스케줄러**: 본인 PC에서 특정 시간마다 실행
2.  **GitHub Actions**: 무료로 클라우드에서 스케줄에 맞춰 실행 (추천)
3.  **Clould VPS**: 서버를 임대하여 24시간 가동
