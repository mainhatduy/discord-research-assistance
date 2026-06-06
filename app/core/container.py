from dependency_injector import containers, providers
from app.core.config import settings
from app.services.pdf_converter import PlaywrightPDFConverter
from app.services.markdown_extractor import PyMuPDFMarkdownExtractor
from app.services.llm_service import GroqLLMService
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
        GroqLLMService,
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL
    )

    research_assistant_service = providers.Singleton(
        ResearchAssistantService,
        pdf_converter=pdf_converter,
        markdown_extractor=markdown_extractor,
        llm_service=llm_service,
        temp_dir=settings.TEMP_DIR
    )
