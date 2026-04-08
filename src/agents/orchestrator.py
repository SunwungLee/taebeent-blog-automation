"""
orchestrator.py
───────────────
전체 블로그 자동화 파이프라인을 총괄하는 메인 Supervisor 에이전트.
6개의 하위 에이전트를 순서대로 실행하고 결과를 전달합니다.

파이프라인 순서:
  1. KeywordSeekerAgent    — 트렌딩 키워드 발굴
  2. KeywordAnalyzerAgent  — 키워드 우선순위 분석
  3. ContentsCreatorAgent  — 콘텐츠 생성 및 편집
  4. PublisherAgent        — Blogger 발행
  5. BlogAnalyzerAgent     — 발행 포스트 성과 분석
"""

import time
from .base_agent import BaseAgent
from .keyword_seeker import KeywordSeekerAgent
from .keyword_analyzer import KeywordAnalyzerAgent
from .contents_creator import ContentsCreatorAgent
from .publisher import PublisherAgent
from .blog_analyzer import BlogAnalyzerAgent


class Orchestrator(BaseAgent):
    """
    전체 자동화 파이프라인의 Supervisor.

    각 하위 에이전트를 순서대로 실행하고,
    이전 에이전트의 결과를 다음 에이전트에 전달합니다.
    """

    def __init__(
        self,
        region: str = "KR",
        keyword_limit: int = 5,
        min_keyword_score: int = 5,
        post_limit: int = 10,
    ):
        super().__init__(name="Orchestrator")
        self.region = region
        self.keyword_limit = keyword_limit
        self.min_keyword_score = min_keyword_score
        self.post_limit = post_limit

        # 하위 에이전트 초기화
        self.keyword_seeker = KeywordSeekerAgent(region=region, limit=keyword_limit)
        self.keyword_analyzer = KeywordAnalyzerAgent(min_score=min_keyword_score)
        self.contents_creator = ContentsCreatorAgent()
        self.publisher = PublisherAgent()
        self.blog_analyzer = BlogAnalyzerAgent(post_limit=post_limit)

    # ──────────────────────────────────────────
    # 단계별 실행 래퍼
    # ──────────────────────────────────────────

    def _run_step(self, step_num: int, label: str, agent: BaseAgent, **kwargs) -> dict:
        """개별 에이전트를 실행하고 결과를 반환하는 공통 래퍼."""
        self.log(f"")
        self.log(f"━━━ Step {step_num}: {label} ━━━")
        try:
            result = agent.run(**kwargs)
            status = "✅ 완료" if result.get("success") else "⚠️  부분 완료"
            self.log(f"Step {step_num} {status}")
            return result
        except Exception as e:
            self.log(f"Step {step_num} ❌ 오류: {e}")
            return {"success": False, "error": str(e)}

    # ──────────────────────────────────────────
    # 공개 인터페이스
    # ──────────────────────────────────────────

    def run(self, **kwargs) -> dict:
        """
        전체 파이프라인 실행.

        Returns:
            {
                "success": bool,
                "steps": dict   # 각 단계별 결과
            }
        """
        self._print_banner()
        start_time = time.time()
        results = {}

        # ── Step 1: 키워드 탐색 ─────────────────────────
        step1 = self._run_step(1, "키워드 탐색 (KeywordSeeker)", self.keyword_seeker)
        results["keyword_seeker"] = step1

        # ── Step 2: 키워드 분석 ─────────────────────────
        # KeywordSeeker가 추가한 토픽은 Sheets에 PENDING으로 저장됨.
        # KeywordAnalyzer가 Sheets에서 직접 PENDING을 가져와 분석.
        step2 = self._run_step(2, "키워드 분석 (KeywordAnalyzer)", self.keyword_analyzer)
        results["keyword_analyzer"] = step2
        passed_topics = step2.get("passed", [])  # 우선순위 통과 토픽

        # ── Step 3: 콘텐츠 생성 ─────────────────────────
        step3 = self._run_step(
            3,
            "콘텐츠 생성 및 편집 (ContentsCreator)",
            self.contents_creator,
            pending_topics=passed_topics if passed_topics else None,
        )
        results["contents_creator"] = step3

        # ── Step 4: 발행 ────────────────────────────────
        step4 = self._run_step(4, "Blogger 발행 (Publisher)", self.publisher)
        results["publisher"] = step4

        # ── Step 5: 성과 분석 ───────────────────────────
        step5 = self._run_step(5, "블로그 성과 분석 (BlogAnalyzer)", self.blog_analyzer)
        results["blog_analyzer"] = step5

        # ── 최종 요약 ────────────────────────────────────
        elapsed = time.time() - start_time
        self._print_summary(results, elapsed)

        return {"success": True, "steps": results}

    # ──────────────────────────────────────────
    # 출력 헬퍼
    # ──────────────────────────────────────────

    def _print_banner(self):
        print("\n" + "=" * 55)
        print("   🤖 Blog Automation System — Multi-Agent Mode")
        print("=" * 55)

    def _print_summary(self, results: dict, elapsed: float):
        print("\n" + "=" * 55)
        print("   📋 실행 요약")
        print("=" * 55)

        seeker = results.get("keyword_seeker", {})
        analyzer = results.get("keyword_analyzer", {})
        creator = results.get("contents_creator", {})
        publisher = results.get("publisher", {})
        blog_analyzer = results.get("blog_analyzer", {})

        print(f"  1. 키워드 탐색   : {len(seeker.get('added_topics', []))}개 신규 토픽 발굴")
        print(f"  2. 키워드 분석   : 통과 {len(analyzer.get('passed', []))}개 / 스킵 {len(analyzer.get('skipped', []))}개")
        print(f"  3. 콘텐츠 생성   : 초안 {creator.get('drafted_count', 0)}개 / 승인 {creator.get('approved_count', 0)}개")
        print(f"  4. 발행          : {publisher.get('published_count', 0)}개 포스트 발행 완료")
        print(f"  5. 성과 분석     : {blog_analyzer.get('posts_analyzed', 0)}개 포스트 분석")
        print(f"\n  ⏱  총 소요 시간: {elapsed:.1f}초")
        print("=" * 55 + "\n")
