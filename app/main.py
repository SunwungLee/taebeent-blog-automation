import argparse
import sys
from .sheets_client import SheetsClient
from .blogger_client import BloggerClient
from .notion_client import NotionClient
from .generator.html_generator import HTMLGenerator
from .generator.validator import ContentValidator
from .services.keyword_service import KeywordService
from .services.post_service import PostService
from .services.publish_service import PublishService
from .utils.logger import logger

def cmd_generate(args):
    """
    Flow:
    read keywords where status = approved_for_writing
    limit to max 3
    mark each as generation_requested
    mark as generating
    generate Blogspot HTML
    validate result
    write to posts sheet
    update keyword status to html_ready
    set post publish_status to ready_to_publish
    """
    sheets = SheetsClient()
    ks = KeywordService(sheets)
    ps = PostService(sheets)
    gen = HTMLGenerator()
    validator = ContentValidator()
    notion = NotionClient()

    candidates = ks.get_generation_candidates(limit=args.limit)
    if not candidates:
        logger.logger.info("No candidates for generation.")
        return

    guidelines = notion.fetch_guidelines()

    for kw in candidates:
        try:
            # Mark state
            ks.mark_generation_requested(kw)
            ks.mark_generating(kw)
            
            # Generate
            content = gen.generate_html_from_keyword(kw, guidelines)
            
            # Validate
            if validator.validate(content):
                # Save to posts and update keyword
                ps.create_post_record_from_generated_content(content)
                ks.mark_html_ready(kw)
                logger.logger.info(f"Successfully generated and validated post for: {kw.main_keyword}")
            else:
                logger.logger.error(f"Validation failed for: {kw.main_keyword}. Reverting status.")
                ks.revert_to_approved(kw)
                
        except Exception as e:
            logger.logger.error(f"Error during generation for {kw.main_keyword}: {e}")
            ks.revert_to_approved(kw)

def cmd_publish(args):
    """
    Flow:
    read posts where publish_status = ready_to_publish
    limit to max 2
    mark as publishing
    publish via Blogger API
    on success:
      publish_status = published
      external_url saved
      keyword status = published
    on failure:
      publish_status = failed
    """
    sheets = SheetsClient()
    blogger = BloggerClient()
    ps = PostService(sheets)
    pbs = PublishService(sheets, blogger, ps)

    candidates = ps.get_publish_candidates(limit=args.limit)
    if not candidates:
        logger.logger.info("No candidates for publishing.")
        return

    for post in candidates:
        try:
            success = pbs.publish_post(post)
            if success:
                logger.logger.info(f"Published post ID: {post.post_id}")
            else:
                logger.logger.error(f"Failed to publish post ID: {post.post_id}")
        except Exception as e:
            logger.logger.error(f"Error during publishing for post ID {post.post_id}: {e}")

def cmd_refresh(args):
    logger.logger.info("Refresh command is not yet fully implemented for MVP.")

def main():
    parser = argparse.ArgumentParser(description="Blogspot Agent System CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate content for keywords")
    gen_parser.add_argument("--limit", type=int, default=3, help="Max number of items to process")

    # Publish command
    pub_parser = subparsers.add_parser("publish", help="Publish ready posts to Blogger")
    pub_parser.add_argument("--limit", type=int, default=2, help="Max number of items to process")

    # Refresh command
    subparsers.add_parser("refresh", help="Refresh/Improve existing posts (Optional)")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "publish":
        cmd_publish(args)
    elif args.command == "refresh":
        cmd_refresh(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
