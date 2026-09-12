import os
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from aiohttp import web

GROQ_API_KEY = "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"
TOKEN = "8817837689:AAGlgQVY3nL-CVd-nhqJ_BnfxLMBIJgWgKM"

# Danh sách ID Telegram được phép dùng bot (Thay số bên dưới bằng ID thật của ní)
ALLOWED_USER_IDS = [123456789] 

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
            model="openai/gpt-oss-20b",
        )
        bot_reply = chat_completion.choices[0].message.content
    except Exception as e:
        bot_reply = "Lỗi kết nối Groq rồi ní ơi!"

    max_length = 4000
    for i in range(0, len(bot_reply), max_length):
        await update.message.reply_text(bot_reply[i:i + max_length])

# Tạo một trang web ảo để Render không bị lỗi cổng mạng
async def handle_web(request):
    return web.Response(text="Bot is running!")

async def main():
    app_web = web.Application()
    app_web.router.add_get("/", handle_web)
    
    # Lấy cổng (port) do Render tự cấp phát
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    # Khởi động Telegram Bot
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT, handle_message))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)
    
    print("Bot và Web server giả lập đã khởi động thành công!")
    
    # Giữ cho chương trình chạy liên tục trên đám mây
    await asyncio.Event().wait()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
