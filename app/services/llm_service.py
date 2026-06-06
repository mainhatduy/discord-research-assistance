from typing import AsyncGenerator
from groq import AsyncGroq
from app.domain.interfaces.llm_service import LLMServiceInterface
from app.core.logger import get_logger

logger = get_logger(__name__)

class GroqLLMService(LLMServiceInterface):
    def __init__(self, api_key: str, model: str):
        self._api_key = api_key
        self._model = model
        # Initialize AsyncGroq client
        self.client = AsyncGroq(api_key=self._api_key)

    async def ask_question_stream(self, context: str, question: str) -> AsyncGenerator[str, None]:
        logger.info(f"Querying Groq LLM using model: {self._model}")
        
        system_prompt = (
            "You are a professional research assistant bot on Discord. "
            "Your task is to analyze the provided article in Markdown format and answer "
            "the user's questions clearly, accurately, and concisely. "
            "Use Markdown formatting (like bullet points, bold text) where appropriate."
        )
        
        user_message = (
            f"Here is the research article in Markdown format:\n\n"
            f"```markdown\n"
            f"{context}\n"
            f"```\n\n"
            f"User's Question: {question}\n\n"
            f"Please provide an answer based only on the provided article."
        )
        
        try:
            completion = await self.client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=1,
                max_completion_tokens=8192,
                top_p=1,
                reasoning_effort="medium",
                stream=True,
                stop=None
            )
            
            async for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                if content:
                    yield content
        except Exception as e:
            logger.error(f"Groq API streaming error: {e}")
            raise e
