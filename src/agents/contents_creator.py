"""
contents_creator.py
────────────────────
PENDING → DRAFTED → APPROVED 전환을 단일 에이전트가 담당.
초안 생성(Writer)과 편집/SEO 최적화(Editor) 두 단계를 내부적으로 처리합니다.

Previous:
  - src/core/content_writer.py  (초안 생성)
  - src/core/editor.py          (편집 및 SEO)
"""

import time
from .base_agent import BaseAgent
from ..integrations.google_sheets import (
    get_pending_topics,
    get_drafted_topics,
    update_topic_status,
    STATUS_DRAFTED,
    STATUS_APPROVED,
)


class ContentsCreatorAgent(BaseAgent):
    """
    콘텐츠 생성 및 편집을 담당하는 에이전트.

    Phase 1 — Write:  PENDING  → 초안 작성 → DRAFTED
    Phase 2 — Edit:   DRAFTED  → 편집/SEO  → APPROVED
    """

    WRITER_SYSTEM = "You are a professional blog content writer specializing in Korean audiences."
    EDITOR_SYSTEM = "You are a meticulous editor, fact-checker, and SEO expert for Korean blogs."

    def __init__(self):
        super().__init__(name="ContentsCreator")

    # ──────────────────────────────────────────
    # Phase 1: 초안 작성
    # ──────────────────────────────────────────

    def _build_write_prompt(self, topic: str, angle: str = "") -> str:
        angle_hint = f"\n추천 관점: {angle}" if angle else ""
        return f"""
다음 토픽에 대한 블로그 포스트 초안을 작성해주세요: "{topic}"{angle_hint}

요구사항:
- 독자의 관심을 끄는 제목 작성
- 명확한 소제목(H2, H3)이 있는 구조화된 구성
- 800~1000단어 분량
- 정보성 있고 전문적이며 읽기 쉬운 톤
- 전체 출력은 반드시 Markdown 형식으로
"""

    def _write_draft(self, topic: str, angle: str = "") -> str | None:
        """토픽에 대한 블로그 초안을 생성한다."""
        self.log(f"초안 작성 중: '{topic}'")
        prompt = self._build_write_prompt(topic, angle)
        result = self.chat(self.WRITER_SYSTEM, prompt)
        if not result:
            self.log(f"초안 생성 실패: '{topic}'")
        return result

    # ──────────────────────────────────────────
    # Phase 2: 편집 및 SEO 최적화
    # ──────────────────────────────────────────

    def _build_edit_prompt(self, draft_content: str) -> str:
        return f"""
아래 블로그 포스트 초안을 검토하고 개선해주세요.

작업:
1. 사실 오류 확인 및 수정
2. 가독성, 문법, 흐름 개선
3. SEO 최적화 (적절한 헤딩 구조, 상단에 메타 설명 추가)
4. 전체 출력은 반드시 Markdown 형식으로

앞뒤 설명 없이 최종 완성된 Markdown 콘텐츠만 반환하세요.

초안 내용:
{draft_content}
"""

    def _edit_draft(self, draft_content: str) -> str | None:
        """초안을 편집하고 SEO 최적화한다."""
        self.log("편집 및 SEO 최적화 중...")
        result = self.chat(self.EDITOR_SYSTEM, self._build_edit_prompt(draft_content))
        if not result:
            self.log("편집 실패")
        return result

    # ──────────────────────────────────────────
    # 내부 처리 루프
    # ──────────────────────────────────────────

    def _process_pending(self, pending_topics: list) -> int:
        """PENDING → DRAFTED 처리."""
        count = 0
        for item in pending_topics:
            topic = item["topic"]
            row_num = item["row_num"]
            angle = item.get("analysis", {}).get("recommended_angle", "")

            draft = self._write_draft(topic, angle)
            if draft:
                success = update_topic_status(row_num, STATUS_DRAFTED, content=draft)
                if success:
                    self.log(f"DRAFTED 완료: '{topic}'")
                    count += 1
                    time.sleep(1)
            else:
                self.log(f"초안 생성 실패 (스킵): '{topic}'")

        return count

    def _process_drafted(self, drafted_topics: list) -> int:
        """DRAFTED → APPROVED 처리."""
        count = 0
        for item in drafted_topics:
            topic = item["topic"]
            row_num = item["row_num"]
            content = item.get("content", "")

            if not content:
                self.log(f"콘텐츠 없음 (스킵): '{topic}'")
                continue

            edited = self._edit_draft(content)
            if edited:
                success = update_topic_status(row_num, STATUS_APPROVED, content=edited)
                if success:
                    self.log(f"APPROVED 완료: '{topic}'")
                    count += 1
                    time.sleep(1)
            else:
                self.log(f"편집 실패 (스킵): '{topic}'")

        return count

    # ──────────────────────────────────────────
    # 공개 인터페이스
    # ──────────────────────────────────────────

    def run(self, pending_topics: list | None = None, **kwargs) -> dict:
        """
        콘텐츠 생성 및 편집 실행.

        Args:
            pending_topics: KeywordAnalyzerAgent가 넘겨준 통과 토픽 목록.
                            None이면 Sheets에서 직접 조회.

        Returns:
            {
                "success": bool,
                "drafted_count": int,
                "approved_count": int,
            }
        """
        self.log("=== 콘텐츠 생성 시작 ===")

        # Phase 1: PENDING → DRAFTED
        pending = pending_topics if pending_topics is not None else get_pending_topics()
        if pending:
            self.log(f"[Phase 1] {len(pending)}개 토픽 초안 작성 시작")
            drafted_count = self._process_pending(pending)
        else:
            self.log("[Phase 1] 처리할 PENDING 토픽 없음")
            drafted_count = 0

        # Phase 2: DRAFTED → APPROVED (항상 Sheets에서 조회)
        drafted = get_drafted_topics()
        if drafted:
            self.log(f"[Phase 2] {len(drafted)}개 초안 편집 시작")
            approved_count = self._process_drafted(drafted)
        else:
            self.log("[Phase 2] 처리할 DRAFTED 토픽 없음")
            approved_count = 0

        self.log(f"완료 — 초안: {drafted_count}개, 승인: {approved_count}개")
        return {
            "success": True,
            "drafted_count": drafted_count,
            "approved_count": approved_count,
        }


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    agent = ContentsCreatorAgent()
    result = agent.run()
    print(result)
