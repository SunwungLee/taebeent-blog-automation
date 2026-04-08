"""
blog_analyzer.py
─────────────────
발행된 블로그 포스트의 성과를 Blogger API로 분석하고
통계 리포트를 출력하는 에이전트. (신규 기능)

주요 분석 항목:
  - 발행된 포스트 목록 조회
  - 조회수, 댓글 수 등 주요 지표 수집
  - GPT를 이용한 콘텐츠 개선 인사이트 제안
"""

import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from .base_agent import BaseAgent
from ..config import get_config

SCOPES = ["https://www.googleapis.com/auth/blogger.readonly"]
TOKEN_PATH = os.path.join("credentials", "token.json")

# 분석할 최근 포스트 수
DEFAULT_POST_LIMIT = 10


class BlogAnalyzerAgent(BaseAgent):
    """
    발행된 블로그 포스트의 성과를 분석하는 에이전트.

    Responsibilities:
      - Blogger API로 최근 발행 포스트 목록 조회
      - 포스트별 조회수·댓글 수 집계
      - GPT 기반 콘텐츠 인사이트 및 개선점 제안
      - 분석 리포트 콘솔 출력
    """

    ANALYZER_SYSTEM = (
        "You are a blog content performance analyst specializing in Korean blogging. "
        "Provide actionable insights based on post titles and engagement data."
    )

    def __init__(self, post_limit: int = DEFAULT_POST_LIMIT):
        super().__init__(name="BlogAnalyzer")
        self.post_limit = post_limit

    # ──────────────────────────────────────────
    # Blogger 인증 (읽기 전용)
    # ──────────────────────────────────────────

    def _authenticate(self):
        """Blogger API 서비스 객체 반환 (읽기 전용 스코프)."""
        creds = None

        if os.path.exists(TOKEN_PATH):
            # 기존 토큰에 readonly 스코프가 포함되어 있으면 재사용
            creds = Credentials.from_authorized_user_file(
                TOKEN_PATH, SCOPES + ["https://www.googleapis.com/auth/blogger"]
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                client_id = get_config("BLOGGER_CLIENT_ID")
                client_secret = get_config("BLOGGER_CLIENT_SECRET")

                if not client_id or not client_secret:
                    self.log("ERROR: Blogger OAuth 자격증명이 .env에 없습니다.")
                    return None

                client_config = {
                    "installed": {
                        "client_id": client_id,
                        "project_id": "blog-automation",
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_secret": client_secret,
                        "redirect_uris": ["http://localhost"],
                    }
                }
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                creds = flow.run_local_server(port=0)

            os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
            with open(TOKEN_PATH, "w") as f:
                f.write(creds.to_json())

        try:
            return build("blogger", "v3", credentials=creds)
        except Exception as e:
            self.log(f"Blogger 서비스 빌드 실패: {e}")
            return None

    # ──────────────────────────────────────────
    # 포스트 데이터 수집
    # ──────────────────────────────────────────

    def _fetch_posts(self, service) -> list[dict]:
        """최근 N개의 Blogger 포스트 데이터를 가져온다."""
        blog_id = get_config("BLOGGER_BLOG_ID")
        if not blog_id:
            self.log("ERROR: BLOGGER_BLOG_ID가 .env에 없습니다.")
            return []

        try:
            response = service.posts().list(
                blogId=blog_id,
                maxResults=self.post_limit,
                status="live",
                fetchBodies=False,  # 본문 불필요, 메타만 수집
            ).execute()
            return response.get("items", [])
        except Exception as e:
            self.log(f"포스트 목록 조회 오류: {e}")
            return []

    def _fetch_post_stats(self, service, post_id: str) -> dict:
        """개별 포스트의 조회수·댓글 수를 조회한다."""
        blog_id = get_config("BLOGGER_BLOG_ID")
        try:
            post = service.posts().get(
                blogId=blog_id, postId=post_id, view="READER"
            ).execute()
            return {
                "views": post.get("customMetaData", {}).get("views", "N/A"),
                "comments": post.get("replies", {}).get("totalItems", 0),
            }
        except Exception:
            return {"views": "N/A", "comments": 0}

    # ──────────────────────────────────────────
    # 분석 및 리포트
    # ──────────────────────────────────────────

    def _generate_insights(self, posts_summary: list[dict]) -> str | None:
        """GPT를 이용해 포스트 성과에 대한 인사이트를 생성한다."""
        if not posts_summary:
            return None

        summary_text = "\n".join(
            f"- 제목: {p['title']} | 댓글: {p['comments']}개 | URL: {p['url']}"
            for p in posts_summary
        )

        prompt = f"""
다음은 최근 블로그 포스트 목록과 참여 지표입니다:

{summary_text}

위 데이터를 기반으로:
1. 독자 참여도가 높은 콘텐츠 유형 분석
2. 앞으로 다뤄야 할 추천 토픽 3가지
3. 콘텐츠 품질 개선을 위한 실행 가능한 인사이트 2~3가지

한국어로 간결하게 작성해주세요.
"""
        return self.chat(self.ANALYZER_SYSTEM, prompt)

    def _print_report(self, posts_summary: list[dict], insights: str | None):
        """분석 결과를 보기 좋게 콘솔에 출력한다."""
        print("\n" + "=" * 60)
        print("  📊 블로그 성과 분석 리포트")
        print("=" * 60)

        if not posts_summary:
            print("  분석할 포스트가 없습니다.")
            return

        print(f"\n  최근 {len(posts_summary)}개 포스트:\n")
        for i, p in enumerate(posts_summary, 1):
            print(f"  {i:2}. {p['title']}")
            print(f"      댓글: {p['comments']}개 | {p['url']}")

        if insights:
            print("\n" + "-" * 60)
            print("  🤖 AI 인사이트:\n")
            print(insights)

        print("\n" + "=" * 60)

    # ──────────────────────────────────────────
    # 공개 인터페이스
    # ──────────────────────────────────────────

    def run(self, **kwargs) -> dict:
        """
        블로그 분석 실행.

        Returns:
            {
                "success": bool,
                "posts_analyzed": int,
                "insights": str | None,
            }
        """
        self.log("=== 블로그 성과 분석 시작 ===")

        service = self._authenticate()
        if not service:
            self.log("인증 실패. 분석을 중단합니다.")
            return {"success": False, "posts_analyzed": 0, "insights": None}

        posts = self._fetch_posts(service)
        if not posts:
            self.log("분석할 포스트가 없습니다.")
            return {"success": True, "posts_analyzed": 0, "insights": None}

        self.log(f"{len(posts)}개 포스트 데이터 수집 중...")
        posts_summary = []
        for post in posts:
            post_id = post.get("id", "")
            title = post.get("title", "제목 없음")
            url = post.get("url", "")
            stats = self._fetch_post_stats(service, post_id)
            posts_summary.append({
                "title": title,
                "url": url,
                "comments": stats["comments"],
                "views": stats["views"],
            })

        self.log("AI 인사이트 생성 중...")
        insights = self._generate_insights(posts_summary)

        self._print_report(posts_summary, insights)

        return {
            "success": True,
            "posts_analyzed": len(posts_summary),
            "insights": insights,
        }


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    agent = BlogAnalyzerAgent()
    result = agent.run()
