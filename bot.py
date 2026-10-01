import asyncio
import json
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, KeyboardButton, Message, ReplyKeyboardMarkup

BOT_TOKEN = os.getenv("BOT_TOKEN", "ТВІЙ_ТОКЕН_ТУТ")
PORT = int(os.environ.get("PORT", 10000))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
FILE = "bot_data.json"

def_data = {
    "food": "🟢 ЩО ТРЕБА ДАВАТИ ЗАРАЗ\nСухе сіно - ГОЛОВНЕ\nТрава, огірки, кабачки, зелень",
    "cleaning": "УБОРКА\nДостаємо Кузю, прибираємо пелюшку, міняємо гамак, насипаємо корм і міняємо воду.",
    "flowers": "цветочки",
}

def load():
    if os.path.exists(FILE):
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return def_data

def save(d):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

main_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="кузя")], [KeyboardButton(text="цветочки")], [KeyboardButton(text="управлять")]], resize_keyboard=True)
kuzya_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="еда"), KeyboardButton(text="уборка")], [KeyboardButton(text="назад")]], resize_keyboard=True)
admin_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="✏️ Їжа"), KeyboardButton(text="✏️ Квіти")], [KeyboardButton(text="✏️ Уборка")], [KeyboardButton(text="назад")]], resize_keyboard=True)
edit_mode = {}

@dp.message(CommandStart())
async def start(m: Message):
    await m.answer("Обирай:", reply_markup=main_kb)

@dp.message(F.text == "назад")
async def back(m: Message):
    edit_mode.pop(m.from_user.id, None)
    await m.answer("Меню:", reply_markup=main_kb)

@dp.message(F.text == "кузя")
async def kuzya(m: Message):
    await m.answer("Кузя:", reply_markup=kuzya_kb)

@dp.message(F.text == "еда")
async def food(m: Message):
    await m.answer(load().get("food"))

@dp.message(F.text == "уборка")
async def cleaning(m: Message):
    await m.answer(load().get("cleaning"))
    try:
        await m.answer_photo(photo=FSInputFile("pelionka.jpg"))
    except:
        pass

@dp.message(F.text == "цветочки")
async def flowers(m: Message):
    await m.answer(load().get("flowers"))

@dp.message(F.text == "управлять")
async def admin(m: Message):
    await m.answer("Вибери, що хочеш змінити:", reply_markup=admin_kb)

@dp.message(F.text == "✏️ Їжа")
async def ef(m: Message):
    edit_mode[m.from_user.id] = "food"
    await m.answer("Напиши новий текст для розділу **їжа**:")

@dp.message(F.text == "✏️ Квіти")
async def efl(m: Message):
    edit_mode[m.from_user.id] = "flowers"
    await m.answer("Напиши новий текст для розділу **квіти**:")

@dp.message(F.text == "✏️ Уборка")
async def ec(m: Message):
    edit_mode[m.from_user.id] = "cleaning"
    await m.answer("Напиши новий текст для розділу **уборка**:")

@dp.message(F.text & ~F.text.in_({"кузя", "цветочки", "управлять", "еда", "уборка", "назад", "✏️ Їжа", "✏️ Квіти", "✏️ Уборка"}))
async def save_text(m: Message):
    uid = m.from_user.id
    if uid in edit_mode:
        target = edit_mode[uid]
        d = load()
        d[target] = m.text
        save(d)
        edit_mode.pop(uid, None)
        await m.answer("✅ Зміни збережено для всіх!", reply_markup=main_kb)

# Простий вебсервер, щоб Render був задоволений і не вимикав сервіс
async def handle(request):
    return web.Response(text="Bot is alive!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

async def main():
    await web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
