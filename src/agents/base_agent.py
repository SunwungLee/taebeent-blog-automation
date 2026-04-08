"""
base_agent.py
─────────────
모든 Agent의 공통 추상 기반 클래스.
각 Agent는 BaseAgent를 상속받아 run() 메서드를 구현합니다.
"""

from abc import ABC, abstractmethod
from openai import OpenAI
from ..config import get_config


class BaseAgent(ABC):
    """
    모든 Agent의 공통 인터페이스.

    Attributes:
        name (str): 에이전트 이름 (로깅용)
    """

    def __init__(self, name: str):
        self.name = name

    # ──────────────────────────────────────────
    # 공통 유틸
    # ──────────────────────────────────────────

    def log(self, message: str):
        """에이전트 이름을 prefix로 붙인 표준 출력 로거."""
        print(f"[{self.name}] {message}")

    def get_openai_client(self) -> OpenAI | None:
        """OpenAI 클라이언트 생성. API 키 없으면 None 반환."""
        api_key = get_config("OPENAI_API_KEY")
        if not api_key:
            self.log("ERROR: OPENAI_API_KEY가 .env에 없습니다.")
            return None
        return OpenAI(api_key=api_key)

    def chat(self, system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini") -> str | None:
        """
        OpenAI Chat Completion 단일 호출 헬퍼.

        Returns:
            응답 텍스트 또는 실패 시 None
        """
        client = self.get_openai_client()
        if not client:
            return None
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            self.log(f"OpenAI API 호출 오류: {e}")
            return None

    # ──────────────────────────────────────────
    # 추상 메서드
    # ──────────────────────────────────────────

    @abstractmethod
    def run(self, **kwargs) -> dict:
        """
        에이전트의 핵심 실행 로직.

        Returns:
            결과를 담은 dict. 최소한 {"success": bool} 포함.
        """
        ...
