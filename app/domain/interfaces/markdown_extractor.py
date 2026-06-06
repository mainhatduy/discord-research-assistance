from abc import ABC, abstractmethod

class MarkdownExtractorInterface(ABC):
    @abstractmethod
    def extract_markdown(self, pdf_path: str) -> str:
        """Extracts text content from a PDF file in Markdown format.

        Args:
            pdf_path (str): The path to the PDF file.

        Returns:
            str: Extracted content in Markdown format.
        """
        pass
