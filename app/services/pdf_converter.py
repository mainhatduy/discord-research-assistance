import os
from playwright.async_api import async_playwright
from app.domain.interfaces.pdf_converter import PDFConverterInterface
from app.core.logger import get_logger

logger = get_logger(__name__)

class PlaywrightPDFConverter(PDFConverterInterface):
    async def convert_to_pdf(self, url: str, output_path: str) -> str:
        logger.info(f"Converting HTML to PDF: {url}")
        
        # Ensure target directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                # Set up a browser page with standard viewport and user agent
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 800}
                )
                page = await context.new_page()
                
                # Go to URL and wait until the network is idle
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Print page as PDF
                await page.pdf(
                    path=output_path,
                    format="Letter",
                    print_background=True,
                    margin={"top": "0.5in", "bottom": "0.5in", "left": "0.5in", "right": "0.5in"}
                )
                logger.info(f"PDF generated successfully and saved to {output_path}")
            except Exception as e:
                logger.error(f"Failed to convert URL to PDF: {e}")
                raise e
            finally:
                await browser.close()
                
        return output_path
