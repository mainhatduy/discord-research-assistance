import os
import uuid
import httpx
from typing import AsyncGenerator
from app.domain.interfaces.pdf_converter import PDFConverterInterface
from app.domain.interfaces.markdown_extractor import MarkdownExtractorInterface
from app.domain.interfaces.llm_service import LLMServiceInterface
from app.core.logger import get_logger

logger = get_logger(__name__)

class ResearchAssistantService:
    def __init__(
        self,
        pdf_converter: PDFConverterInterface,
        markdown_extractor: MarkdownExtractorInterface,
        llm_service: LLMServiceInterface,
        temp_dir: str
    ):
        self._pdf_converter = pdf_converter
        self._markdown_extractor = markdown_extractor
        self._llm_service = llm_service
        self._temp_dir = temp_dir
        
        # Ensure temp directory exists
        os.makedirs(self._temp_dir, exist_ok=True)

    async def _download_pdf(self, url: str, target_path: str) -> str:
        logger.info(f"Downloading PDF directly from: {url}")
        async with httpx.AsyncClient(follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            with open(target_path, "wb") as f:
                f.write(response.content)
        return target_path

    async def process_research_stream(self, url: str, question: str) -> AsyncGenerator[str, None]:
        # Generate unique temporary file name
        session_id = str(uuid.uuid4())
        pdf_path = os.path.join(self._temp_dir, f"{session_id}.pdf")
        
        try:
            # Step 1: Obtain the PDF
            # Check if direct PDF link or arXiv pdf endpoint
            is_pdf = url.lower().endswith(".pdf") or "arxiv.org/pdf/" in url.lower()
            
            if is_pdf:
                yield "📥 Đang tải PDF trực tiếp...\n"
                await self._download_pdf(url, pdf_path)
            else:
                yield "⏳ Đang kết nối và chuyển đổi liên kết thành file PDF bằng Playwright...\n"
                await self._pdf_converter.convert_to_pdf(url, pdf_path)
                
            # Step 2: Extract Markdown from PDF
            yield "📝 Đang trích xuất nội dung bài báo sang Markdown...\n"
            markdown_content = self._markdown_extractor.extract_markdown(pdf_path)
            
            if not markdown_content.strip():
                raise ValueError("Nội dung trích xuất từ tài liệu bị rỗng.")
                
            # Step 3: Query the LLM and stream response
            yield "🤖 Đang xử lý câu hỏi với Groq LLM (gpt-oss-120b)...\n\n"
            async for chunk in self._llm_service.ask_question_stream(markdown_content, question):
                yield chunk
                
        except Exception as e:
            logger.error(f"Error in ResearchAssistantService: {e}")
            yield f"\n❌ Đã xảy ra lỗi trong quá trình xử lý: {str(e)}"
        finally:
            # Clean up temp PDF file
            if os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                    logger.info(f"Cleaned up temporary file: {pdf_path}")
                except Exception as e:
                    logger.warning(f"Could not delete temporary file {pdf_path}: {e}")
