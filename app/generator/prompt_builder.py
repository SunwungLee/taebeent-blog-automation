from ..models import KeywordRow

class PromptBuilder:
    def __init__(self):
        pass

    def build_content_prompt(self, kw: KeywordRow, guidelines: str = "") -> str:
        """
        Builds a prompt for generating Blogspot HTML content.
        """
        content_type = kw.content_type
        keyword = kw.main_keyword
        
        prompt = f"""
Write a high-quality blog post for Blogspot in HTML format about '{keyword}'.
The content type is '{content_type}'.

Guidelines:
{guidelines}

Structure Requirements:
1. Start with an <h2> containing a overview of {keyword}.
2. Include at least 3 more <h2> sections covering different aspects (e.g., benefits, how-to, tips).
3. Use <h3> for sub-sections where appropriate.
4. Final <h2> must be '자주 묻는 질문' (FAQ) containing at least 2 Q&A pairs.
5. Use <p> for short paragraphs.
6. NO markdown in the output. PURE HTML string only.
7. Tone: Informative, friendly, NO aggressive CTA or promotional language.

SEO: Use the keyword '{keyword}' naturally in headings and paragraphs.
"""
        return prompt.strip()
