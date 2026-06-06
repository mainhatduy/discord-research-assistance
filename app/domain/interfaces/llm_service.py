from abc import ABC, abstractmethod
from typing import AsyncGenerator

class LLMServiceInterface(ABC):
    @abstractmethod
    async def ask_question_stream(self, context: str, question: str) -> AsyncGenerator[str, None]:
        """Queries the LLM with context and a question, streaming back the response chunks.

        Args:
            context (str): The context information (Markdown article).
            question (str): The user's question about the context.

        Yields:
            str: Response text chunks from the LLM.
        """
        pass
