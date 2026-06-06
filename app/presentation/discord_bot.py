import re
import time
import discord
from app.services.research_assistant import ResearchAssistantService
from app.core.logger import get_logger

logger = get_logger(__name__)

class ResearchAssistantBot(discord.Client):
    def __init__(self, research_assistant_service: ResearchAssistantService, *args, **kwargs):
        # Enable message content intent
        intents = discord.Intents.default()
        intents.message_content = True
        kwargs["intents"] = intents
        
        super().__init__(*args, **kwargs)
        self._research_assistant_service = research_assistant_service
        self._url_pattern = re.compile(r'(https?://[^\s]+)')

    async def on_ready(self):
        logger.info(f"Bot logged in as {self.user} (ID: {self.user.id})")
        logger.info("Bot is ready to process research links!")

    async def on_message(self, message: discord.Message):
        # Ignore messages from the bot itself
        if message.author.bot:
            return

        # Check for URL in the message
        match = self._url_pattern.search(message.content)
        if not match:
            # If the bot is mentioned directly and there's no URL, send help text
            if self.user in message.mentions:
                await message.reply(
                    "👋 Xin chào! Tôi là Trợ Lý Nghiên Cứu Khoa Học.\n"
                    "Hãy gửi tôi một liên kết bài báo (HTML hoặc PDF) kèm theo câu hỏi của bạn. "
                    "Tôi sẽ chuyển đổi nội dung bài báo và trả lời câu hỏi đó.\n\n"
                    "**Ví dụ:**\n"
                    "https://arxiv.org/pdf/2605.16120v1 Tóm tắt các đóng góp chính của bài báo này."
                )
            return

        url = match.group(0)
        
        # Extract the question by removing the URL and any bot mentions
        question = message.content.replace(url, "")
        if self.user in message.mentions:
            question = question.replace(f"<@{self.user.id}>", "").replace(f"<@!{self.user.id}>", "")
        question = question.strip()

        # Default question if none is provided
        if not question:
            question = "Hãy tóm tắt nội dung chính của bài báo này."

        logger.info(f"Processing request from {message.author} | URL: {url} | Question: {question}")

        # Send initial status message
        status_msg = await message.reply("⏳ Đang tiếp nhận yêu cầu và tải nội dung bài báo...")

        response_text = ""
        last_edit_time = time.time()
        current_message = status_msg

        try:
            async for chunk in self._research_assistant_service.process_research_stream(url, question):
                response_text += chunk
                now = time.time()
                
                # Update message if 1.5 seconds have passed, or if the text limit is exceeded
                if now - last_edit_time > 1.5 or len(response_text) > 1900:
                    if len(response_text) > 1900:
                        split_idx = response_text.rfind("\n", 0, 1900)
                        if split_idx == -1 or split_idx < 1000:
                            split_idx = 1900
                        
                        chunk_to_send = response_text[:split_idx]
                        response_text = response_text[split_idx:]
                        
                        await current_message.edit(content=chunk_to_send)
                        current_message = await message.channel.send(
                            response_text if response_text else "⏳ Đang tiếp tục xử lý..."
                        )
                        last_edit_time = time.time()
                    else:
                        await current_message.edit(content=response_text)
                        last_edit_time = time.time()
                        
            # Send final remaining chunk if any
            if response_text:
                await current_message.edit(content=response_text)
                
        except Exception as e:
            logger.error(f"Error while processing and sending response: {e}")
            error_message = f"\n❌ Đã xảy ra lỗi hệ thống khi gửi tin nhắn: {str(e)}"
            if len(response_text) + len(error_message) <= 2000:
                await current_message.edit(content=response_text + error_message)
            else:
                await message.channel.send(error_message)
