import sys
from app.core.config import settings
from app.core.container import Container
from app.presentation.discord_bot import ResearchAssistantBot
from app.core.logger import get_logger

logger = get_logger(__name__)

def main():
    logger.info("Starting Discord Research Assistant Bot...")
    
    # Check if DISCORD_BOT_TOKEN is set
    if not settings.DISCORD_BOT_TOKEN:
        logger.error("Error: DISCORD_BOT_TOKEN environment variable is not set!")
        print("\n[CRITICAL ERROR] DISCORD_BOT_TOKEN is not set in your .env file.")
        print("Please add 'DISCORD_BOT_TOKEN=your_token_here' to the .env file in the project root.\n")
        sys.exit(1)

    # Check if GEMINI_API_KEY is set
    if not settings.GEMINI_API_KEY:
        logger.error("Error: GEMINI_API_KEY environment variable is not set!")
        print("\n[CRITICAL ERROR] GEMINI_API_KEY is not set in your .env file.")
        print("Please add 'GEMINI_API_KEY=your_key_here' to the .env file in the project root.\n")
        sys.exit(1)

    # Initialize Dependency Injection Container
    container = Container()
    
    # Resolve the ResearchAssistantService
    research_assistant_service = container.research_assistant_service()
    
    # Create the Discord bot client with the service dependency injected
    bot = ResearchAssistantBot(research_assistant_service=research_assistant_service)
    
    try:
        bot.run(settings.DISCORD_BOT_TOKEN)
    except Exception as e:
        logger.error(f"Failed to run the bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
