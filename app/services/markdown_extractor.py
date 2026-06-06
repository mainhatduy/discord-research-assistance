import pymupdf4llm
from app.domain.interfaces.markdown_extractor import MarkdownExtractorInterface
from app.core.logger import get_logger

logger = get_logger(__name__)

class PyMuPDFMarkdownExtractor(MarkdownExtractorInterface):
    def extract_markdown(self, pdf_path: str) -> str:
        logger.info(f"Extracting Markdown from PDF: {pdf_path}")
        try:
            # pymupdf4llm.to_markdown reads the PDF and returns Markdown text
            markdown_content = pymupdf4llm.to_markdown(pdf_path)
            logger.info(f"Extracted {len(markdown_content)} characters of Markdown content")
            return markdown_content
        except Exception as e:
            logger.error(f"Error during PDF to Markdown extraction: {e}")
            raise e
