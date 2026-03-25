import google.generativeai as genai
import os
from openai import OpenAI
from ..config import GEMINI_API_KEY, OPENAI_API_KEY
from ..models import GeneratedContent, KeywordRow
from ..utils.logger import logger
from .prompt_builder import PromptBuilder

class HTMLGenerator:
    def __init__(self):
        self.gemini_available = bool(GEMINI_API_KEY)
        if self.gemini_available:
            genai.configure(api_key=GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
        
        self.openai_available = bool(OPENAI_API_KEY)
        if self.openai_available:
            self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
        if not self.gemini_available and not self.openai_available:
            raise ValueError("No LLM API keys (Gemini or OpenAI) found in environment variables")
            
        self.prompt_builder = PromptBuilder()

    def generate_html_from_keyword(self, kw: KeywordRow, guidelines: str = "") -> GeneratedContent:
        """
        Generates blog content using available LLM and parses it into a GeneratedContent model.
        """
        prompt = self.prompt_builder.build_content_prompt(kw, guidelines)
        
        # Try Gemini first
        if self.gemini_available:
            try:
                logger.logger.info(f"Generating content for keyword (Gemini): {kw.main_keyword}")
                response = self.gemini_model.generate_content(prompt)
                return GeneratedContent(
                    keyword_id=kw.keyword_id,
                    title=kw.main_keyword,
                    html=response.text.strip(),
                    faq="Included in HTML",
                    content_type=kw.content_type
                )
            except Exception as e:
                logger.logger.warning(f"Gemini generation failed: {e}. Trying OpenAI fallback...")
        
        # Fallback to OpenAI
        if self.openai_available:
            try:
                logger.logger.info(f"Generating content for keyword (OpenAI): {kw.main_keyword}")
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )
                full_text = response.choices[0].message.content.strip()
                return GeneratedContent(
                    keyword_id=kw.keyword_id,
                    title=kw.main_keyword,
                    html=full_text,
                    faq="Included in HTML",
                    content_type=kw.content_type
                )
            except Exception as e:
                logger.log_action("OpenAI Generation", keyword_id=kw.keyword_id, success=False, error_message=str(e))
                raise
        
        raise Exception("Failed to generate content with any available LLM.")
