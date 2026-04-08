"""
keyword_analyzer.py
────────────────────
PENDING 상태의 키워드를 GPT로 분석하여 블로그 포스팅 우선순위를
평가하고, 낮은 우선순위 토픽은 SKIPPED 처리하는 에이전트.

Note:
  실제 검색량 API(Naver, Google Search Console 등)가 없으므로
  GPT의 판단을 기반으로 우선순위를 산정합니다.
  향후 실제 API로 교체할 수 있도록 _score_topic()을 분리했습니다.
"""

import json
import time
from .base_agent import BaseAgent
from ..integrations.google_sheets import (
    get_pending_topics,
    update_topic_status,
)

# Google Sheets에 없는 신규 상태 — 낮은 우선순위 키워드 스킵
STATUS_SKIPPED = "SKIPPED"
# 분석 통과 → 그대로 PENDING 유지 (ContentsCreator가 처리)
MIN_SCORE = 5  # 10점 만점 기준, 이 미만이면 SKIP


class KeywordAnalyzerAgent(BaseAgent):
    """
    PENDING 토픽의 블로그 포스팅 가치를 평가하는 에이전트.

    Responsibilities:
      - PENDING 토픽 목록 조회
      - GPT를 이용한 트렌드/경쟁도/독자 관심도 종합 점수 산출
      - MIN_SCORE 미만 토픽은 SKIPPED 처리
      - 통과 토픽 목록 반환 (Orchestrator가 ContentsCreator에 전달)
    """

    SYSTEM_PROMPT = (
        "You are a professional blog content strategist and SEO expert. "
        "Evaluate the given Korean blog topic and return a JSON response."
    )

    def __init__(self, min_score: int = MIN_SCORE):
        super().__init__(name="KeywordAnalyzer")
        self.min_score = min_score

    # ──────────────────────────────────────────
    # 내부 메서드
    # ──────────────────────────────────────────

    def _score_topic(self, topic: str) -> dict:
        """
        GPT를 이용해 토픽의 블로그 가치를 평가한다.

        Returns:
            {
                "score": int (1~10),
                "reason": str,
                "recommended_angle": str
            }
        """
        user_prompt = f"""
다음 블로그 토픽을 평가해주세요: "{topic}"

아래 기준으로 종합 점수(1~10)를 매겨주세요:
- 독자 관심도 및 검색 수요
- 블로그 콘텐츠화 적합성 (너무 짧거나 논란성이 큰 주제는 감점)
- 정보성/교육성 가치
- 한국 독자 대상 관련성

반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
{{
  "score": <1~10 정수>,
  "reason": "<평가 이유 1-2문장>",
  "recommended_angle": "<이 토픽을 블로그로 풀어낼 추천 관점>"
}}
"""
        result_text = self.chat(self.SYSTEM_PROMPT, user_prompt)
        if not result_text:
            return {"score": 0, "reason": "API 오류", "recommended_angle": ""}

        try:
            # JSON 블록만 추출 (GPT가 ```json ... ``` 형태로 줄 수 있음)
            clean = result_text.strip()
            if clean.startswith("```"):
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean.strip())
        except Exception as e:
            self.log(f"JSON 파싱 오류 ({topic}): {e}")
            return {"score": 0, "reason": "파싱 오류", "recommended_angle": ""}

    # ──────────────────────────────────────────
    # 공개 인터페이스
    # ──────────────────────────────────────────

    def run(self, pending_topics: list | None = None, **kwargs) -> dict:
        """
        키워드 분석 실행.

        Args:
            pending_topics: 외부에서 주입된 PENDING 목록 (없으면 Sheets에서 직접 조회)

        Returns:
            {
                "success": bool,
                "passed": list[dict],   # MIN_SCORE 이상 → ContentsCreator로 넘김
                "skipped": list[str],   # MIN_SCORE 미만 → SKIPPED 처리됨
            }
        """
        self.log("=== 키워드 분석 시작 ===")

        topics = pending_topics if pending_topics is not None else get_pending_topics()
        if not topics:
            self.log("분석할 PENDING 토픽이 없습니다.")
            return {"success": True, "passed": [], "skipped": []}

        self.log(f"{len(topics)}개 토픽 분석 중...")
        passed = []
        skipped = []

        for item in topics:
            topic = item["topic"]
            self.log(f"  분석 중: '{topic}'")

            analysis = self._score_topic(topic)
            score = analysis.get("score", 0)
            reason = analysis.get("reason", "")
            angle = analysis.get("recommended_angle", "")

            self.log(f"  → 점수: {score}/10 | {reason}")

            if score < self.min_score:
                self.log(f"  → SKIP (점수 {score} < 기준 {self.min_score})")
                update_topic_status(item["row_num"], STATUS_SKIPPED)
                skipped.append(topic)
            else:
                self.log(f"  → PASS | 추천 관점: {angle}")
                # 분석 결과를 item에 추가해서 ContentsCreator에 전달
                item["analysis"] = analysis
                passed.append(item)

            time.sleep(0.5)  # API rate limit 방어

        self.log(f"분석 완료 — 통과: {len(passed)}개, 스킵: {len(skipped)}개")
        return {"success": True, "passed": passed, "skipped": skipped}


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    agent = KeywordAnalyzerAgent()
    result = agent.run()
    print(result)
