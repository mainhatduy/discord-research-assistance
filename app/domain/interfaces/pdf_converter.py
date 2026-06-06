from abc import ABC, abstractmethod

class PDFConverterInterface(ABC):
    @abstractmethod
    async def convert_to_pdf(self, url: str, output_path: str) -> str:
        """Converts an HTML webpage to a PDF file.

        Args:
            url (str): The URL of the webpage to convert.
            output_path (str): The file path where the PDF will be saved.

        Returns:
            str: The path to the saved PDF file.
        """
        pass
