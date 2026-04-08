"""
main.py — Blog Automation System 진입점

Orchestrator를 통해 전체 멀티 에이전트 파이프라인을 실행합니다.

파이프라인:
  KeywordSeeker → KeywordAnalyzer → ContentsCreator → Publisher → BlogAnalyzer
"""

from dotenv import load_dotenv

# .env 로드는 가장 먼저
load_dotenv()

from src.integrations.google_sheets import init_sheet_headers
from src.agents import Orchestrator


def main():
    # 시트 헤더 초기화 (최초 1회)
    init_sheet_headers()

    # Orchestrator 설정
    orchestrator = Orchestrator(
        region="KR",           # 구글 뉴스 지역
        keyword_limit=5,       # 탐색할 최대 키워드 수
        min_keyword_score=5,   # 콘텐츠 생성 최소 점수 (10점 만점)
        post_limit=10,         # 성과 분석할 최근 포스트 수
    )

    # 전체 파이프라인 실행
    orchestrator.run()


if __name__ == "__main__":
    main()
