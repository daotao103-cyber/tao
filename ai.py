import os
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    print(f"--> Nhận tin nhắn từ Telegram: {user_message}")
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message,
                }
            ],
            model="openai/gpt-oss-20b",
        )
        bot_reply = chat_completion.choices[0].message.content
    except Exception as e:
        print(f"--> Lỗi gọi Groq API: {e}")
        bot_reply = "Lỗi kết nối rồi ní ơi, kiểm tra lại giúp anh nhé!"

    max_length = 4000
    for i in range(0, len(bot_reply), max_length):
        chunk = bot_reply[i:i + max_length]
        await update.message.reply_text(chunk)

if __name__ == '__main__':
    TELEGRAM_TOKEN = "8817837689:AAGlgQVY3nL-CVd-nhqJ_BnfxLMBIJgWgKM"
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    print("Bot Telegram chạy siêu mô hình OpenAI GPT-OSS đã sẵn sàng...")
    app.run_polling()