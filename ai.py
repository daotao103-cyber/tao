import os
import asyncio
import aiohttp
from groq import Groq
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from aiohttp import web

GROQ_API_KEY = "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"
TOKEN = "8982539903:AAH42KwxKz4EH4uMRz-RWmQNvuMD83FYfLw"
ALLOWED_USER_IDS = [8341514824] 

client = Groq(api_key=GROQ_API_KEY)
telegram_app = None

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

async def handle_webhook(request):
    try:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)
        return web.Response(text="OK")
    except Exception as e:
        print(f"Lỗi xử lý Webhook: {e}")
        return web.Response(text="Error", status=500)

async def handle_web(request):
    return web.Response(text="Bot is active!")

async def main():
    global telegram_app
    
    # 1. Ép xóa sạch webhook cũ trước khi khởi động qua HTTP API trực tiếp
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true") as resp:
            print("Đã dọn sạch webhook cũ trên Telegram:", await resp.text())

    # 2. Khởi tạo ứng dụng Telegram
    telegram_app = ApplicationBuilder().token(TOKEN).build()
    telegram_app.add_handler(MessageHandler(filters.TEXT, handle_message))
    await telegram_app.initialize()
    await telegram_app.start()

    # 3. Đăng ký Webhook mới với URL của Render
    render_url = os.environ.get("RENDER_EXTERNAL_URL")
    if render_url:
        webhook_url = f"{render_url}/webhook"
        await telegram_app.bot.set_webhook(url=webhook_url)
        print(f"Đã gán Webhook mới tại: {webhook_url}")

    # 4. Chạy Web Server aiohttp để nhận request từ Render và Telegram
    app = web.Application()
    app.router.add_get("/", handle_web)
    app.router.add_post("/webhook", handle_webhook)
    
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    print(f"Server đã mở thành công trên cổng {port}!")
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
