import time
from openai import OpenAI
from ..config import get_config
from ..integrations.google_sheets import update_topic_status, STATUS_DRAFTED

def get_client():
    api_key = get_config("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY is missing in .env")
        return None
    return OpenAI(api_key=api_key)

def generate_draft(topic):
    client = get_client()
    if not client:
        return None
        
    print(f"Generating draft for topic: '{topic}'...")
    
    prompt = f"""
    You are an expert professional blog content writer.
    Please write an engaging, highly informative, and well-researched blog post about the following topic: "{topic}".
    
    Requirements:
    - Write an attention-grabbing title.
    - Create a structured outline with clear headings.
    - Write approximately 800-1000 words.
    - The tone should be informative, engaging, and professional.
    - Provide the output completely in Markdown format.
    """
    
    try:
        # Using gpt-4o-mini which is fast, cheap and high quality
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional blog writer."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating content via OpenAI: {e}")
        return None

def process_pending_topics(pending_topics):
    processed_count = 0
    for item in pending_topics:
        topic = item['topic']
        row_num = item['row_num']
        
        draft = generate_draft(topic)
        if draft:
            success = update_topic_status(row_num, STATUS_DRAFTED, content=draft)
            if success:
                print(f"Successfully drafted topic: {topic}")
                processed_count += 1
                # OpenAI has much better rate limits, 1s delay is enough
                time.sleep(1)
        else:
            print(f"Failed to draft topic: {topic}")
            
    return processed_count
