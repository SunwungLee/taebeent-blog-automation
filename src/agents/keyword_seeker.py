"""
keyword_seeker.py
─────────────────
Google News RSS를 크롤링하여 트렌딩 키워드(토픽)를 발굴하고
Google Sheets에 PENDING 상태로 저장하는 에이전트.

Previous: src/core/trend_analyzer.py
"""

import feedparser
from .base_agent import BaseAgent
from ..integrations.google_sheets import add_new_topic


class KeywordSeekerAgent(BaseAgent):
    """
    트렌딩 키워드를 발굴하는 에이전트.

    Responsibilities:
      - Google News RSS로부터 최신 뉴스 토픽 수집
      - 중복 제거 후 Google Sheets에 PENDING으로 등록
    """

    DEFAULT_RSS_URL = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"

    def __init__(self, region: str = "KR", limit: int = 5):
        super().__init__(name="KeywordSeeker")
        self.region = region
        self.limit = limit

    # ──────────────────────────────────────────
    # 내부 메서드
    # ──────────────────────────────────────────

    def _fetch_news_topics(self) -> list[str]:
        """Google News RSS에서 뉴스 제목 목록을 가져온다."""
        self.log(f"Google News RSS 크롤링 중... ({self.DEFAULT_RSS_URL})")
        try:
            feed = feedparser.parse(self.DEFAULT_RSS_URL)
            if not feed.entries:
                self.log("RSS 피드에 항목이 없습니다.")
                return []

            topics = []
            for entry in feed.entries:
                # 제목 끝의 " - 언론사" 부분 제거
                clean_title = entry.title.split(" - ")[0].strip()
                topics.append(clean_title)

            self.log(f"{len(topics)}개 뉴스 토픽 수집 완료.")
            return topics
        except Exception as e:
            self.log(f"RSS 크롤링 오류: {e}")
            return []

    def _store_topics(self, topics: list[str]) -> list[str]:
        """발굴한 토픽을 Google Sheets에 저장하고, 성공적으로 추가된 토픽 목록을 반환."""
        added = []
        count = 0
        for topic in topics:
            if count >= self.limit:
                break
            success = add_new_topic(topic)
            if success:
                added.append(topic)
                count += 1

        self.log(f"Sheets에 {len(added)}개 신규 토픽 등록 완료.")
        return added

    # ──────────────────────────────────────────
    # 공개 인터페이스
    # ──────────────────────────────────────────

    def run(self, **kwargs) -> dict:
        """
        키워드 탐색 실행.

        Returns:
            {
                "success": bool,
                "added_topics": list[str]   # 새로 Sheets에 등록된 토픽
            }
        """
        self.log("=== 키워드 탐색 시작 ===")
        topics = self._fetch_news_topics()

        if not topics:
            self.log("수집된 토픽이 없습니다.")
            return {"success": False, "added_topics": []}

        added = self._store_topics(topics)
        return {"success": True, "added_topics": added}


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    agent = KeywordSeekerAgent(region="KR", limit=5)
    result = agent.run()
    print(result)
