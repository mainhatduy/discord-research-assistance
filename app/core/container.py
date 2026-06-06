from dependency_injector import containers, providers
from app.core.config import settings
from app.services.pdf_converter import PlaywrightPDFConverter
from app.services.markdown_extractor import PyMuPDFMarkdownExtractor
from app.services.llm_service import GeminiLLMService
from app.services.research_assistant import ResearchAssistantService

class Container(containers.DeclarativeContainer):
    # Base configuration
    config = providers.Configuration()

    # Core service providers
    pdf_converter = providers.Singleton(
        PlaywrightPDFConverter
    )

    markdown_extractor = providers.Singleton(
        PyMuPDFMarkdownExtractor
    )

    llm_service = providers.Singleton(
        GeminiLLMService,
        api_key=settings.GEMINI_API_KEY,
        primary_model=settings.GEMINI_PRIMARY_MODEL,
        fallback_model=settings.GEMINI_FALLBACK_MODEL
    )

    research_assistant_service = providers.Singleton(
        ResearchAssistantService,
        pdf_converter=pdf_converter,
        markdown_extractor=markdown_extractor,
        llm_service=llm_service,
        temp_dir=settings.TEMP_DIR
    )
