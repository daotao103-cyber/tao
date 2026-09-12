import os
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

GROQ_API_KEY = "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"
TOKEN = "8982539903:AAH42KwxKz4EH4uMRz-RWmQNvuMD83FYfLw"

ALLOWED_USER_IDS = [8341514824] 

client = Groq(api_key=GROQ_API_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ALLOWED_USER_IDS:
        await update.message.reply_text("Xin lỗi, ní không có quyền sử dụng bot này!")
        return

    user_message = update.message.text
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": user_message}],
            model="llama-3.1-8b-instant",
        )
        bot_reply = chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Lỗi Groq: {e}")
        bot_reply = "Lỗi kết nối Groq rồi ní ơi!"

    max_length = 4000
    for i in range(0, len(bot_reply), max_length):
        await update.message.reply_text(bot_reply[i:i + max_length])

def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    port = int(os.environ.get("PORT", 10000))
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    
    if render_url:
        webhook_url = f"{render_url}/webhook"
        print(f"Khởi động Bot qua Webhook chính thức tại: {webhook_url}")
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path="webhook",
            webhook_url=webhook_url,
            drop_pending_updates=True
        )
    else:
        print("Khởi động Bot qua Polling...")
        application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
