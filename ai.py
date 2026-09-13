import os
import asyncio
from aiohttp import web
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

GROQ_API_KEY = "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"
TOKEN = "8982539903:AAH42KwxKz4EH4uMRz-RWmQNvuMD83FYfLw"
ALLOWED_USER_IDS = [8341514824] 

client = Groq(api_key=GROQ_API_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username or update.message.from_user.first_name
    print(f"🎯 Nhận tin từ {user_name} ({user_id}): {update.message.text}")

    if user_id not in ALLOWED_USER_IDS:
        await update.message.reply_text(f"Xin lỗi, ID của ní ({user_id}) không được phép dùng bot!")
        return

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": update.message.text}],
            model="llama-3.1-8b-instant",
        )
        bot_reply = chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Lỗi Groq: {e}")
        bot_reply = "Lỗi kết nối Groq rồi ní ơi!"

    max_length = 4000
    for i in range(0, len(bot_reply), max_length):
        await update.message.reply_text(bot_reply[i:i + max_length])
    print("✅ Đã phản hồi thành công!")

# Web server giả lập để giữ cổng cho Render không bị ngủ đông
async def handle_web(request):
    return web.Response(text="Bot is running with polling!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_web)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server giữ cổng đã chạy trên port {port}")

async def main():
    # 1. Khởi động web server phụ để giữ cổng
    await start_web_server()

    # 2. Khởi chạy Telegram Bot bằng Polling
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    print("Bot đang khởi động Polling...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    # Giữ cho chương trình chạy liên tục
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
