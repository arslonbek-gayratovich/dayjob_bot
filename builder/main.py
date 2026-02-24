
#YANGISI
# ================== YANGISI (MISOLLAR BILAN) ==================

import asyncio
import logging
import re
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import KeyboardButton, InlineKeyboardButton

# ================== СОЗЛАМАЛАР ==================
API_TOKEN = '8361270725:AAHe4uiGMDJ998ZjffeZ94D5uu5axU8F49o'
CHANNEL_ID = -1003829181382  # Каналингиз ИД-си (албатта манфий сон)
CHANNEL_URL = "https://t.me/dayjob_khujand/19"

PHONE_REGEX = r"^\d{9}$"
DATE_REGEX = r"^\d{2}\.\d{2}\.\d{4}$"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ================== ТОҶИКИСТОН МАНЗИЛЛАРИ ==================
TAJIKISTAN_LOCATIONS = [
    "Душанбе","Ваҳдат","Ҳисор","Шаҳринав","Варзоб","Рӯдакӣ",
    "Хуҷанд","Бӯстон","Гулистон","Истаравшан","Исфара","Конибодом",
    "Панҷакент","Ашт","Спитамен","Ҷаббор Расулов","Зафаробод","Шаҳристон","Айнӣ",
    "Бохтар","Кӯлоб","Левакант","Норак","Ёвон","Вахш","Данғара",
    "Фархор","Ҳамадонӣ","Ҷайҳун","Ҷалолиддини Балхӣ","Қубодиён",
    "Муъминобод","Темурмалик","Хуросон","Шаҳритус","Носири Хусрав",
    "Хоруғ","Рӯшон","Шуғнон","Ишкошим","Мурғоб","Ванҷ","Дарвоз",
    "Рашт","Тоҷикобод","Лахш","Нуробод","Сангвор"
]

def location_keyboard():
    kb = ReplyKeyboardBuilder()
    for loc in TAJIKISTAN_LOCATIONS:
        kb.button(text=loc)
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

# ================== FSM ==================
class EmployerStates(StatesGroup):
    date = State()
    work_time = State()
    work_type = State()
    description = State()
    location_main = State()
    location_extra = State()
    price = State()
    name = State()
    contact = State()

# ================== МЕНЮ ==================
def main_menu():
    kb = ReplyKeyboardBuilder()
    kb.row(
        KeyboardButton(text="👷‍♂️ Коргар"),
        KeyboardButton(text="💼 Кордиҳанда")
    )
    return kb.as_markup(resize_keyboard=True)

# ================== START ==================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "<b>Ассалому алайкум!</b>\n\n"
        "🤝 Dayjob — платформа барои пайваст кардани коргар ва кордиҳанда.\n\n"
        "Лутфан интихоб кунед:",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

# ================== КОРГАР ==================
@dp.message(F.text == "👷‍♂️ Коргар")
async def worker_handler(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="📢 Дидани эълонҳо", url=CHANNEL_URL))
    await message.answer(
        "Барои дидани ҷойҳои кори дастрас ба канал гузаред:",
        reply_markup=kb.as_markup()
    )

# ================== КОРДИҲАНДА ==================
@dp.message(F.text == "💼 Кордиҳанда")
async def employer_start(message: types.Message, state: FSMContext):
    kb = ReplyKeyboardBuilder()
    kb.row(
        KeyboardButton(text="Имрӯз"),
        KeyboardButton(text="Пагоҳ"),
        KeyboardButton(text="Дигар рӯз")
    )
    await message.answer(
        "📅 <b>Санаи корро интихоб кунед</b>\n"
        "Мисол:\n"
        "• Имрӯз\n"
        "• Пагоҳ\n"
        "• Дигар рӯз",
        reply_markup=kb.as_markup(resize_keyboard=True),
        parse_mode="HTML"
    )
    await state.set_state(EmployerStates.date)

@dp.message(EmployerStates.date)
async def step_date(message: types.Message, state: FSMContext):
    today = datetime.now()

    if message.text == "Имрӯз":
        date_str = today.strftime("%d.%m.%Y")
    elif message.text == "Пагоҳ":
        date_str = (today + timedelta(days=1)).strftime("%d.%m.%Y")
    elif message.text == "Дигар рӯз":
        await message.answer(
            "📅 <b>Санаи корро ворид кунед</b>\n"
            "Мисол: 25.02.2026",
            reply_markup=types.ReplyKeyboardRemove(),
            parse_mode="HTML"
        )
        return
    else:
        if not re.match(DATE_REGEX, message.text):
            await message.answer("❌ Формати сана нодуруст аст.\nМисол: 25.02.2026")
            return
        date_str = message.text

    await state.update_data(date=date_str)

    await message.answer(
        "⏰ <b>Соатҳои кор</b>\n"
        "Мисол:\n"
        "• 09:00–18:00\n"
        "• 08:00–17:00\n"
        "• то анҷоми кор",
        parse_mode="HTML"
    )
    await state.set_state(EmployerStates.work_time)

@dp.message(EmployerStates.work_time)
async def step_time(message: types.Message, state: FSMContext):
    # ⏰ Вақт — ОДДИЙ STRING, ҲЕЧ ҚАНДАЙ FORMAT ТЕКШИРУВИ ЙЎҚ
    await state.update_data(work_time=message.text)

    await message.answer(
        "🛠 <b>Намуди корро ворид намоед</b>\n"
        "Мисол:\n"
        "• усто\n"
        "• боркаш\n"
        "• электрик\n"
        "• сантехник",
        parse_mode="HTML"
    )
    await state.set_state(EmployerStates.work_type)

@dp.message(EmployerStates.work_type)
async def step_type(message: types.Message, state: FSMContext):
    await state.update_data(work_type=message.text)
    await message.answer(
        "📝 <b>Тавсифи кӯтоҳи корро нависед</b>\n"
        "Мисол:\n"
        "• Таъмири хонаи 2-ҳуҷрагӣ\n"
        "• Боркашонӣ барои 1 рӯз\n"
        "• Иваз кардани қубур",
        parse_mode="HTML"
    )
    await state.set_state(EmployerStates.description)

@dp.message(EmployerStates.description)
async def step_desc(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        "📍 <b>Шаҳр ё ноҳияро интихоб кунед</b>\n"
        "Мисол: Душанбе, Хуҷанд, Бохтар",
        reply_markup=location_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(EmployerStates.location_main)

@dp.message(EmployerStates.location_main)
async def step_location_main(message: types.Message, state: FSMContext):
    if message.text not in TAJIKISTAN_LOCATIONS:
        await message.answer("❗ Лутфан танҳо аз рӯйхат интихоб намоед.")
        return

    await state.update_data(location_main=message.text)
    await message.answer(
        "➕ <b>Қисми иловагии суроға</b>\n"
        "Мисол:\n"
        "• 32 микроноҳия\n"
        "• кӯчаи Сомонӣ",
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode="HTML"
    )
    await state.set_state(EmployerStates.location_extra)

@dp.message(EmployerStates.location_extra)
async def step_location_extra(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(location=f"{data['location_main']}, {message.text}")

    kb = ReplyKeyboardBuilder()
    kb.row(
        KeyboardButton(text="Дар сӯҳбат"),
        KeyboardButton(text="Бо даст менависам")
    )
    await message.answer(
        "💰 <b>Музди меҳнат</b>\n"
        "Мисол:\n"
        "• 200 сомонӣ\n"
        "• 300 сомонӣ\n"
        "• Дар сӯҳбат",
        reply_markup=kb.as_markup(resize_keyboard=True),
        parse_mode="HTML"
    )
    await state.set_state(EmployerStates.price)

@dp.message(EmployerStates.price)
async def step_price(message: types.Message, state: FSMContext):
    if message.text == "Бо даст менависам":
        await message.answer(
            "💰 <b>Музди меҳнатро ворид кунед</b>\n"
            "Мисол: 250 сомонӣ",
            reply_markup=types.ReplyKeyboardRemove(),
            parse_mode="HTML"
        )
        return

    await state.update_data(price=message.text)
    await message.answer(
        "👤 <b>Номи худро ворид кунед</b>\n"
        "Мисол:\n"
        "• Али\n"
        "• Муҳаммад",
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode="HTML"
    )
    await state.set_state(EmployerStates.name)

@dp.message(EmployerStates.name)
async def step_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📱 Фиристодани рақам", request_contact=True))
    await message.answer(
        "📞 <b>Рақами тамос</b>\n"
        "Мисол:\n"
        "• 987654321",
        reply_markup=kb.as_markup(resize_keyboard=True),
        parse_mode="HTML"
    )
    await state.set_state(EmployerStates.contact)

@dp.message(EmployerStates.contact)
async def step_contact(message: types.Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    elif message.text and re.match(PHONE_REGEX, message.text):
        phone = message.text
    else:
        await message.answer("❌ Рақами телефон нодуруст аст.\nМисол: 987654321")
        return

    data = await state.get_data()

    text = (
        f"🆕 <b>ЭЪЛОНИ НАВ</b>\n\n"
        f"📅 <b>Сана:</b> {data['date']}\n"
        f"⏰ <b>Вақт:</b> {data['work_time']}\n"
        f"🛠 <b>Кор:</b> {data['work_type']}\n"
        f"📝 <b>Тавсиф:</b> {data['description']}\n"
        f"📍 <b>Суроға:</b> {data['location']}\n"
        f"💰 <b>Музд:</b> {data['price']}\n"
        f"👤 <b>Номи кордиҳанда:</b> {data['name']}\n"
        f"📞 <b>Телефон:</b> {phone}\n"
    )

    await bot.send_message(CHANNEL_ID, text, parse_mode="HTML")

    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="📢 Эълонҳоро дар канал дидан", url=CHANNEL_URL))

    await message.answer(
        "✅ <b>Эълон бо муваффақият фиристода шуд!</b>",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )
    await state.clear()

# ================== FALLBACK ==================
@dp.message(F.text, ~F.state)
async def fallback(message: types.Message):
    await message.answer(
        "Лутфан аз меню истифода баред 👇",
        reply_markup=main_menu()
    )

# ================== MAIN ==================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



