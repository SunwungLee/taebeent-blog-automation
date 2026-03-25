import time
from openai import OpenAI
from ..config import get_config
from ..integrations.google_sheets import update_topic_status, STATUS_APPROVED

def get_client():
    api_key = get_config("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

def edit_and_fact_check(draft_content):
    client = get_client()
    if not client:
        return None
        
    print("Editing and fact-checking content...")
    
    prompt = f"""
    You are a meticulous Editor, Fact-Checker, and SEO Expert.
    Review the following blog post draft.
    
    Tasks:
    1. Check for factual inaccuracies and correct them if possible.
    2. Improve readability, grammar, and flow.
    3. Optimize for SEO (ensure headings are proper, add a short meta description at the top).
    4. Ensure the entire response is formatted perfectly in Markdown.
    
    Return ONLY the final, polished Markdown content, ready for publishing without any conversational text before or after.
    
    Draft Content:
    {draft_content}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional editor and SEO expert."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error editing content via OpenAI: {e}")
        return None

def process_drafted_topics(drafted_topics):
    processed_count = 0
    for item in drafted_topics:
        topic = item['topic']
        row_num = item['row_num']
        content = item.get('content')
        
        if not content:
            continue
            
        edited_content = edit_and_fact_check(content)
        if edited_content:
            success = update_topic_status(row_num, STATUS_APPROVED, content=edited_content)
            if success:
                print(f"Successfully edited & approved topic: {topic}")
                processed_count += 1
                time.sleep(1)
                
    return processed_count
