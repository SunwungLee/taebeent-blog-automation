"""
publisher.py
────────────
APPROVED 상태의 콘텐츠를 Blogger API를 통해 발행하고
Google Sheets 상태를 PUBLISHED로 업데이트하는 에이전트.

Previous: src/core/publisher.py
"""

import os
import markdown as md_lib
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from .base_agent import BaseAgent
from ..config import get_config
from ..integrations.google_sheets import (
    get_approved_topics,
    update_topic_status,
    STATUS_PUBLISHED,
)

SCOPES = ["https://www.googleapis.com/auth/blogger"]
TOKEN_PATH = os.path.join("credentials", "token.json")


class PublisherAgent(BaseAgent):
    """
    Blogger에 콘텐츠를 발행하는 에이전트.

    Responsibilities:
      - Blogger OAuth 인증 처리 (토큰 캐싱)
      - Markdown → HTML 변환 후 포스트 업로드
      - Sheets 상태를 PUBLISHED로 업데이트
    """

    def __init__(self):
        super().__init__(name="Publisher")

    # ──────────────────────────────────────────
    # Blogger 인증
    # ──────────────────────────────────────────

    def _authenticate(self):
        """Blogger OAuth2 인증 후 서비스 객체 반환."""
        creds = None

        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                client_id = get_config("BLOGGER_CLIENT_ID")
                client_secret = get_config("BLOGGER_CLIENT_SECRET")

                if not client_id or not client_secret:
                    self.log("ERROR: BLOGGER_CLIENT_ID 또는 BLOGGER_CLIENT_SECRET이 .env에 없습니다.")
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
            service = build("blogger", "v3", credentials=creds)
            return service
        except Exception as e:
            self.log(f"Blogger 서비스 빌드 실패: {e}")
            return None

    # ──────────────────────────────────────────
    # 발행
    # ──────────────────────────────────────────

    def _publish_post(self, service, title: str, content_md: str) -> str | None:
        """
        Markdown 콘텐츠를 HTML로 변환하여 Blogger에 포스트로 발행.

        Returns:
            발행된 포스트 URL 또는 실패 시 None
        """
        blog_id = get_config("BLOGGER_BLOG_ID")
        if not blog_id:
            self.log("ERROR: BLOGGER_BLOG_ID가 .env에 없습니다.")
            return None

        html_content = md_lib.markdown(content_md)
        body = {
            "kind": "blogger#post",
            "title": title,
            "content": html_content,
        }

        try:
            response = service.posts().insert(
                blogId=blog_id, body=body, isDraft=False
            ).execute()
            return response.get("url")
        except Exception as e:
            self.log(f"Blogger 발행 오류 ('{title}'): {e}")
            return None

    # ──────────────────────────────────────────
    # 공개 인터페이스
    # ──────────────────────────────────────────

    def run(self, **kwargs) -> dict:
        """
        콘텐츠 발행 실행.

        Returns:
            {
                "success": bool,
                "published_count": int,
                "published_urls": list[str],
            }
        """
        self.log("=== 발행 시작 ===")

        approved = get_approved_topics()
        if not approved:
            self.log("발행할 APPROVED 토픽이 없습니다.")
            return {"success": True, "published_count": 0, "published_urls": []}

        service = self._authenticate()
        if not service:
            self.log("Blogger 인증 실패. 발행을 중단합니다.")
            return {"success": False, "published_count": 0, "published_urls": []}

        self.log(f"{len(approved)}개 토픽 발행 시작...")
        published_count = 0
        published_urls = []

        for item in approved:
            topic = item["topic"]
            row_num = item["row_num"]
            content = item.get("content", "")

            if not content:
                self.log(f"콘텐츠 없음 (스킵): '{topic}'")
                continue

            self.log(f"발행 중: '{topic}'")
            url = self._publish_post(service, title=topic, content_md=content)

            if url:
                success = update_topic_status(row_num, STATUS_PUBLISHED, url=url)
                if success:
                    self.log(f"발행 완료: '{topic}' → {url}")
                    published_count += 1
                    published_urls.append(url)
            else:
                self.log(f"발행 실패: '{topic}'")

        self.log(f"발행 완료 — {published_count}개 포스트 업로드됨")
        return {
            "success": True,
            "published_count": published_count,
            "published_urls": published_urls,
        }


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    agent = PublisherAgent()
    result = agent.run()
    print(result)
