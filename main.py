import os
from dotenv import load_dotenv

# Load env variables before importing local modules
load_dotenv()

from src.integrations.google_sheets import init_sheet_headers, get_pending_topics, get_drafted_topics, get_approved_topics
from src.core.trend_analyzer import analyze_and_store_trends
from src.core.content_writer import process_pending_topics
from src.core.editor import process_drafted_topics
from src.core.publisher import process_approved_topics

def main():
    print("==========================================")
    print("    Starting Blog Automation System       ")
    print("==========================================\n")
    
    # Initialize Headers if needed (first run)
    init_sheet_headers()
    
    print("== Step 1: Analyzing trends -> Google Sheets ==")
    # Find new trending topics and append them to the sheet (Limit to 3 for testing)
    analyze_and_store_trends(region='KR', limit=3)
    
    print("\n== Step 2: Drafting content using Gemini API ==")
    pending = get_pending_topics()
    if pending:
        print(f"Found {len(pending)} pending topics.")
        process_pending_topics(pending)
    else:
        print("No pending topics to process.")
        
    print("\n== Step 3: Editing and fact-checking content ==")
    drafted = get_drafted_topics()
    if drafted:
        print(f"Found {len(drafted)} drafted topics.")
        process_drafted_topics(drafted)
    else:
        print("No drafted topics to process.")
        
    print("\n== Step 4: Publishing to Blogger ==")
    approved = get_approved_topics()
    if approved:
        print(f"Found {len(approved)} approved topics.")
        process_approved_topics(approved)
    else:
        print("No approved topics to publish.")
        
    print("\n==========================================")
    print("               Finished!                  ")
    print("==========================================")

if __name__ == "__main__":
    main()
