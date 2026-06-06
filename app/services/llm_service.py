from typing import AsyncGenerator
from google import genai
from google.genai import types
from google.genai import errors
from app.domain.interfaces.llm_service import LLMServiceInterface
from app.core.logger import get_logger

logger = get_logger(__name__)

class GeminiLLMService(LLMServiceInterface):
    def __init__(self, api_key: str, primary_model: str, fallback_model: str):
        self._api_key = api_key
        self._primary_model = primary_model
        self._fallback_model = fallback_model
        # Initialize Google GenAI client
        self.client = genai.Client(api_key=self._api_key)

    async def ask_question_stream(self, context: str, question: str) -> AsyncGenerator[str, None]:
        logger.info(f"Querying Gemini LLM. Primary: {self._primary_model}, Fallback: {self._fallback_model}")
        
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
        
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=user_message),
                ],
            ),
        ]
        
        generate_content_config = types.GenerateContentConfig(
            temperature=0.7,
            system_instruction=[
                types.Part.from_text(text=system_prompt),
            ],
        )

        yielded_any = False
        try:
            logger.info(f"Attempting to generate content stream using primary model: {self._primary_model}")
            async with self.client.aio as aclient:
                response = await aclient.models.generate_content_stream(
                    model=self._primary_model,
                    contents=contents,
                    config=generate_content_config,
                )
                async for chunk in response:
                    if chunk.text:
                        yielded_any = True
                        yield chunk.text
        except errors.APIError as e:
            # Check if quota limit was hit (429) and we haven't yielded anything yet.
            if e.code == 429 and not yielded_any:
                logger.warning(
                    f"Primary model {self._primary_model} hit quota limit (429). "
                    f"Swapping to fallback model {self._fallback_model}..."
                )
                yield "⚠️ *Đã đạt giới hạn quota của Gemini 3.5. Đang tự động chuyển sang Gemini 3.1 Flash Lite...*\n\n"
                try:
                    async with self.client.aio as aclient:
                        response = await aclient.models.generate_content_stream(
                            model=self._fallback_model,
                            contents=contents,
                            config=generate_content_config,
                        )
                        async for chunk in response:
                            if chunk.text:
                                yield chunk.text
                except Exception as inner_e:
                    logger.error(f"Fallback model {self._fallback_model} also failed: {inner_e}")
                    raise inner_e
            else:
                logger.error(f"Gemini API error with code {e.code}: {e.message}")
                raise e
        except Exception as e:
            logger.error(f"Gemini API unexpected streaming error: {e}")
            raise e
