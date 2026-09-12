import os
import asyncio
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from aiohttp import web

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
            model="llama-3.1-8b-instant",  # Đã sửa lại đúng tên model của Groq
        )
        bot_reply = chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Lỗi Groq: {e}")
        bot_reply = "Lỗi kết nối Groq rồi ní ơi!"

    max_length = 4000
    for i in range(0, len(bot_reply), max_length):
        await update.message.reply_text(bot_reply[i:i + max_length])

async def handle_web(request):
    return web.Response(text="Bot is running!")

async def main():
    app_web = web.Application()
    app_web.router.add_get("/", handle_web)
    
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    print("Bot và Web server giả lập đã khởi động thành công!")
    
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
