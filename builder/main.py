'''
import asyncio
import logging
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton

# СОЗЛАМАЛАР
API_TOKEN = '8361270725:AAHe4uiGMDJ998ZjffeZ94D5uu5axU8F49o'
CHANNEL_ID = -1003829181382  # Каналингиз ИД-си (албатта манфий сон)
CHANNEL_URL = "https://t.me/dayjob_khujand/19" # Канал линки


# Рақамни текшириш учун Regex (Халқаро формат)
#PHONE_REGEX = r"^\+?9?9?2?\d{9}$"
PHONE_REGEX = r"^\+992\d{9}$"
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class EmployerStates(StatesGroup):
    work_type = State()
    description = State()
    location = State()
    price = State()
    work_time = State()
    contact = State()

def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="👷‍♂️ Ишчи"), KeyboardButton(text="💼 Иш берувчи"))
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "<b>Ассалому алайкум!</b>\n\n"
        "🇹🇯 <b>Dayjob</b> — ин на танҳо даромад, балки роҳ ба сӯи шукуфоии оила ва амалӣ шудани орзуҳои шумост! "
        "Мо инҷо ҳастем, то меҳнати шумо арзанда қадр шавад ва ҳар як сомониву дираме, ки меёбед, "
        "ба хонадони шумо баракату шодмонӣ орад. Биёед, ба сӯи хушбахтии оила ва рушди шахсӣ якҷо қадам занем.\n\n"
        "🇺🇿 <b>Dayjob</b> — bu nafaqat daromad, balki oilangiz farovonligi va orzulari sari yo‘ldir! "
        "Sizning mehnatingiz munosib qadrlanishi, har bir topgan so‘mingiz xonadoningizga baraka va quvonch "
        "olib kelishi uchun biz shu yerdamiz. Oila baxti va shaxsiy yuksalish sari birgalikda qadam tashlaymiz.\n\n"
        "<b>Ким сифатида давом этмоқчисиз?</b>",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

# --- ИШЧИ ҚИСМИ ---
@dp.message(F.text == "👷‍♂️ Ишчи")
async def worker_handler(message: types.Message):
    try:
        user_status = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id)
        if user_status.status in ["member", "administrator", "creator"]:
            await message.answer(f"Сиз каналга аъзосиз! Эълонларни бу ерда кўришингиз мумкин: {CHANNEL_URL}")
        else:
            builder = InlineKeyboardBuilder()
            builder.row(InlineKeyboardButton(text="Каналга аъзо бўлиш", url=CHANNEL_URL))
            await message.answer("Эълонларни кўриш учун аввал каналга аъзо бўлишингиз керак!", reply_markup=builder.as_markup())
    except Exception as e:
        logging.error(f"Хатолик: {e}")
        await message.answer("Канал билан боғланишда хатолик юз берди. Илтимос, кейинроқ уриниб кўринг.")

# --- ИШ БЕРУВЧИ ҚИСМИ ---
@dp.message(F.text == "💼 Иш берувчи")
async def employer_start(message: types.Message, state: FSMContext):
    await message.answer("Иш турини киритинг (масалан: Уста, Юк ташувчи...):", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(EmployerStates.work_type)

@dp.message(EmployerStates.work_type)
async def process_type(message: types.Message, state: FSMContext):
    await state.update_data(work_type=message.text)
    await message.answer("Иш ҳақида батафсил маълумот беринг:")
    await state.set_state(EmployerStates.description)

@dp.message(EmployerStates.description)
async def process_desc(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Иш жойлашган жой (манзил):")
    await state.set_state(EmployerStates.location)

@dp.message(EmployerStates.location)
async def process_loc(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer("Иш ҳақи (нархи):")
    await state.set_state(EmployerStates.price)

@dp.message(EmployerStates.price)
async def process_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("Иш вақти (масалан: Бугун 09:00 дан 18:00 гача):")
    await state.set_state(EmployerStates.work_time)

@dp.message(EmployerStates.work_time)
async def process_time(message: types.Message, state: FSMContext):
    await state.update_data(work_time=message.text)
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📱 Контактни юбориш", request_contact=True))
    await message.answer("Боғланиш учун рақамингизни юборинг ёки қўлда ёзинг (масалан: +992921234567):",
                         reply_markup=builder.as_markup(resize_keyboard=True))
    await state.set_state(EmployerStates.contact)

# --- КОНТАКТНИ ҚАБУЛ ҚИЛИШ (ТУГМА ЁКИ МАТН) ---
@dp.message(EmployerStates.contact)
async def process_contact(message: types.Message, state: FSMContext):
    phone = None

    if message.contact:
        phone = message.contact.phone_number
    elif message.text and re.match(PHONE_REGEX, message.text):
        phone = message.text
    else:
        await message.answer("Илтимос, рақамни тўғри форматда киритинг ёки тугмани босинг!")
        return

    data = await state.get_data()
    user_mention = message.from_user.mention_html()

    text = (
        f"🆕 <b>ЯНГИ ЭЪЛОН!</b>\n\n"
        f"🛠 <b>Иш тури:</b> {data['work_type']}\n"
        f"📝 <b>Маълумот:</b> {data['description']}\n"
        f"📍 <b>Манзил:</b> {data['location']}\n"
        f"💰 <b>Нархи:</b> {data['price']}\n"
        f"⏰ <b>Иш вақти:</b> {data['work_time']}\n"
        f"📞 <b>Алоқа:</b> {phone}\n"
        f"👤 <b>Эълон берувчи:</b> {user_mention}"
    )

    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="HTML")
        await message.answer(f"Эълонингиз каналга жойлаштирилди!  {CHANNEL_URL}", reply_markup=main_menu())
        await state.clear()
    except Exception as e:
        logging.error(f"Каналга юборишда хато: {e}")
        await message.answer("Хатолик юз берди. Канал ID ва бот админлигини текширинг.", reply_markup=main_menu())

# --- КУТИЛМАГАН ХАБАРЛАРНИ ТУТИШ ---
@dp.message()
async def echo_handler(message: types.Message):
    await message.answer("Тушунарсиз буйруқ. Илтимос, менюдаги тугмалардан фойдаланинг.", reply_markup=main_menu())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())'''


#tojikcha varianti
import asyncio
import logging
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import KeyboardButton, InlineKeyboardButton

# ================== СОЗЛАМАЛАР ==================
API_TOKEN = '8361270725:AAHe4uiGMDJ998ZjffeZ94D5uu5axU8F49o'
CHANNEL_ID = -1003829181382  # Каналингиз ИД-си (албатта манфий сон)
CHANNEL_URL = "https://t.me/dayjob_khujand/19" # Канал линки

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
    work_type = State()
    description = State()
    location_main = State()
    location_extra = State()
    date = State()
    price = State()
    work_time = State()
    name = State()      # 👤 yangi
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
    await message.answer(
        "🛠 <b>Намуди корро ворид намоед</b>\n"
        "Масалан: усто, боркаш, электрик",
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode="HTML"
    )
    await state.set_state(EmployerStates.work_type)

@dp.message(EmployerStates.work_type)
async def step_type(message: types.Message, state: FSMContext):
    await state.update_data(work_type=message.text)
    await message.answer(
        "📝 <b>Тавсифи кӯтоҳи корро нависед</b>",
        parse_mode="HTML"
    )
    await state.set_state(EmployerStates.description)

@dp.message(EmployerStates.description)
async def step_desc(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        "📍 <b>Шаҳр ё ноҳияро интихоб кунед</b>",
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
        "Масалан: 32 мкр, кӯчаи Сомонӣ",
        reply_markup=types.ReplyKeyboardRemove(),
        parse_mode="HTML"
    )
    await state.set_state(EmployerStates.location_extra)

@dp.message(EmployerStates.location_extra)
async def step_location_extra(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(location=f"{data['location_main']}, {message.text}")

    await message.answer(
        "📅 <b>Санаи кор (танҳо 1 рӯз)</b>\n"
        "Мисол: 25.02.2026",
        parse_mode="HTML"
    )
    await state.set_state(EmployerStates.date)

@dp.message(EmployerStates.date)
async def step_date(message: types.Message, state: FSMContext):
    if not re.match(DATE_REGEX, message.text):
        await message.answer("❌ Формати сана нодуруст аст. Мисол: 25.02.2026")
        return

    await state.update_data(date=message.text)
    await message.answer(
        "💰 <b>Музди меҳнат</b>\n"
        "Масалан: 200 сомонӣ ё мувофиқа мешавад",
        parse_mode="HTML"
    )
    await state.set_state(EmployerStates.price)

@dp.message(EmployerStates.price)
async def step_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer(
        "⏰ <b>Соатҳои кор</b>\n"
        "Масалан: 09:00–18:00 ё то анҷоми кор",
        parse_mode="HTML"
    )
    await state.set_state(EmployerStates.work_time)

@dp.message(EmployerStates.work_time)
async def step_time(message: types.Message, state: FSMContext):
    await state.update_data(work_time=message.text)
    await message.answer(
        "👤 <b>Номи худро ворид кунед</b>\n"
        "Масалан: Муҳаммад, Али",
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
        "📞 <b>Рақами тамос</b>",
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
        await message.answer("❌ Рақами телефон нодуруст аст.")
        return

    data = await state.get_data()
    user = message.from_user.mention_html()

    text = (
        f"🆕 <b>ЭЪЛОНИ НАВ</b>\n\n"
        f"👤 <b>Номи кордиҳанда:</b> {data['name']}\n"
        f"🛠 <b>Кор:</b> {data['work_type']}\n"
        f"📝 <b>Тавсиф:</b> {data['description']}\n"
        f"📍 <b>Суроға:</b> {data['location']}\n"
        f"📅 <b>Сана:</b> {data['date']}\n"
        f"💰 <b>Музд:</b> {data['price']}\n"
        f"⏰ <b>Вақт:</b> {data['work_time']}\n"
        f"📞 <b>Телефон:</b> {phone}\n"
    )

    await bot.send_message(CHANNEL_ID, text, parse_mode="HTML")

    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(
            text="📢 Эълонни каналда кўриш",
            url=CHANNEL_URL
        )
    )

    await message.answer(
        "✅ <b>Эълон бо муваффақият фиристода шуд!</b>",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )
    await state.clear()

# ================== FALLBACK ==================
@dp.message()
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

#YANGISI
'''import asyncio
import logging
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import KeyboardButton, InlineKeyboardButton

# ================== СОЗЛАМАЛАР ==================
API_TOKEN = ""          # <-- token qo‘ying
CHANNEL_ID = 0          # <-- kanal ID (masalan: -100xxxxxxxxxx)
CHANNEL_URL = "https://t.me/dayjob_khujand/19"

PHONE_REGEX = r"^\+992\d{9}$"
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ================== МАНЗИЛҲОИ ТОҶИКИСТОН ==================
TAJIKISTAN_LOCATIONS = [
    # Душанбе
    "Душанбе", "Ваҳдат", "Ҳисор", "Рӯдакӣ", "Варзоб", "Шаҳринав",

    # Суғд
    "Хуҷанд", "Бӯстон", "Гулистон", "Истаравшан", "Исфара",
    "Конибодом", "Панҷакент", "Ашт", "Спитамен",
    "Ҷаббор Расулов", "Зафаробод",

    # Хатлон
    "Бохтар", "Кӯлоб", "Левакант", "Норак", "Ёвон", "Вахш",
    "Данғара", "Фархор", "Ҳамадонӣ", "Ҷайҳун",
    "Ҷалолиддини Балхӣ", "Қубодиён", "Муъминобод",
    "Темурмалик", "Хуросон", "Шаҳритус",

    # ВМКБ
    "Хоруғ", "Рӯшон", "Шуғнон", "Ишкошим", "Мурғоб", "Ванҷ", "Дарвоз",

    # НТҶ
    "Рашт", "Тоҷикобод", "Лахш", "Нуробод", "Сангвор"
]

def location_keyboard():
    builder = ReplyKeyboardBuilder()
    for loc in TAJIKISTAN_LOCATIONS:
        builder.button(text=loc)
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# ================== FSM ==================
class EmployerStates(StatesGroup):
    work_type = State()
    description = State()
    location = State()
    price = State()
    work_time = State()
    contact = State()

# ================== МЕНЮ ==================
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="👷‍♂️ Коргар"),
        KeyboardButton(text="💼 Кор диҳанда")
    )
    return builder.as_markup(resize_keyboard=True)

# ================== START ==================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "<b>Ассалому алайкум!</b>\n\n"
        "🇹🇯 <b>Dayjob</b> — платформа барои ёфтани кор ва коргар.\n\n"
        "<b>Ким сифатида давом медиҳед?</b>",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

# ================== КОРГАР ==================
@dp.message(F.text == "👷‍♂️ Коргар")
async def worker_handler(message: types.Message):
    try:
        member = await bot.get_chat_member(CHANNEL_ID, message.from_user.id)
        if member.status in ["member", "administrator", "creator"]:
            await message.answer(f"Эълонҳоро дар ин ҷо бинед:\n{CHANNEL_URL}")
        else:
            kb = InlineKeyboardBuilder()
            kb.row(InlineKeyboardButton(text="Ба канал аъзо шудан", url=CHANNEL_URL))
            await message.answer(
                "Барои дидани эълонҳо аввал ба канал аъзо шавед.",
                reply_markup=kb.as_markup()
            )
    except Exception as e:
        logging.error(e)
        await message.answer("Хатогӣ бо канал.")

# ================== КОР ДИҲАНДА ==================
@dp.message(F.text == "💼 Кор диҳанда")
async def employer_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Намуди корро нависед (масалан: Усто, боркаш):",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(EmployerStates.work_type)

@dp.message(EmployerStates.work_type)
async def step_type(message: types.Message, state: FSMContext):
    await state.update_data(work_type=message.text)
    await message.answer("Маълумоти кӯтоҳ дар бораи кор:")
    await state.set_state(EmployerStates.description)

@dp.message(EmployerStates.description)
async def step_desc(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        "📍 Манзилро аз рӯйхат интихоб кунед:",
        reply_markup=location_keyboard()
    )
    await state.set_state(EmployerStates.location)

@dp.message(EmployerStates.location)
async def step_location(message: types.Message, state: FSMContext):
    if message.text not in TAJIKISTAN_LOCATIONS:
        await message.answer("❗ Лутфан манзилро аз рӯйхат интихоб кунед.")
        return

    await state.update_data(location=message.text)
    await message.answer(
        "Нарх (масалан: 200 ё музокира мешавад):",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(EmployerStates.price)

@dp.message(EmployerStates.price)
async def step_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("Вақти кор (масалан: 09:00-18:00):")
    await state.set_state(EmployerStates.work_time)

@dp.message(EmployerStates.work_time)
async def step_time(message: types.Message, state: FSMContext):
    await state.update_data(work_time=message.text)
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📱 Рақамро фиристед", request_contact=True))
    await message.answer(
        "Рақами тамосро фиристед ё нависед (+992XXXXXXXX):",
        reply_markup=kb.as_markup(resize_keyboard=True)
    )
    await state.set_state(EmployerStates.contact)

@dp.message(EmployerStates.contact)
async def step_contact(message: types.Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    elif message.text and re.match(PHONE_REGEX, message.text):
        phone = message.text
    else:
        await message.answer("Рақам нодуруст!")
        return

    data = await state.get_data()
    user = message.from_user.mention_html()

    text = (
        f"🆕 <b>ЭЪЛОНИ НАВ</b>\n\n"
        f"🛠 <b>Кор:</b> {data['work_type']}\n"
        f"📝 <b>Маълумот:</b> {data['description']}\n"
        f"📍 <b>Манзил:</b> {data['location']}\n"
        f"💰 <b>Нарх:</b> {data['price']}\n"
        f"⏰ <b>Вақт:</b> {data['work_time']}\n"
        f"📞 <b>Тамос:</b> {phone}\n"
        f"👤 <b>Кор диҳанда:</b> {user}"
    )

    try:
        await bot.send_message(CHANNEL_ID, text, parse_mode="HTML")
        await message.answer(
            f"Эълон ба канал фиристода шуд!\n{CHANNEL_URL}",
            reply_markup=main_menu()
        )
        await state.clear()
    except Exception as e:
        logging.error(e)
        await message.answer("Хатогӣ ҳангоми фиристодан.")

# ================== FALLBACK ==================
@dp.message()
async def fallback(message: types.Message):
    await message.answer(
        "Лутфан аз меню истифода баред.",
        reply_markup=main_menu()
    )

# ================== MAIN ==================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


import asyncio
import logging
import re
import sqlite3
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import KeyboardButton, InlineKeyboardButton

# ================== SOZLAMALAR ==================
API_TOKEN = '8361270725:AAHe4uiGMDJ998ZjffeZ94D5uu5axU8F49o'
CHANNEL_ID = -1003829181382  # Каналингиз ИД-си (албатта манфий сон)
CHANNEL_URL = "https://t.me/dayjob_khujand"

ADMIN_ID = 5971651215          # o'zingni Telegram ID

PHONE_REGEX = r"^\+?9?9?2?\d{9}$"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ================== DATABASE ==================
db = sqlite3.connect("dayjob.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    role TEXT,
    joined_at TEXT,
    free_until TEXT,
    payment_status INTEGER DEFAULT 0,
    warned INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employer_id INTEGER,
    work_type TEXT,
    description TEXT,
    location TEXT,
    price TEXT,
    work_time TEXT,
    contact TEXT,
    created_at TEXT,
    payment_status INTEGER DEFAULT 0
)
""")

db.commit()

# ================== FSM ==================
class EmployerStates(StatesGroup):
    work_type = State()
    description = State()
    location = State()
    price = State()
    work_time = State()
    contact = State()

# ================== MENYU ==================
def main_menu():
    kb = ReplyKeyboardBuilder()
    kb.row(
        KeyboardButton(text="👷‍♂️ Ишчи"),
        KeyboardButton(text="💼 Иш берувчи")
    )
    return kb.as_markup(resize_keyboard=True)

# ================== START ==================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Ассалому алайкум!\n\n"
        "Ким сифатида давом этасиз?",
        reply_markup=main_menu()
    )

# ================== ISHCHI ==================
@dp.message(F.text == "👷‍♂️ Ишчи")
async def worker_handler(message: types.Message):

    cursor.execute("""
    INSERT OR IGNORE INTO users
    (id, username, full_name, role, joined_at, free_until)
    VALUES (?, ?, ?, 'worker', ?, ?)
    """, (
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name,
        datetime.now().strftime("%Y-%m-%d"),
        (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
    ))
    db.commit()

    try:
        member = await bot.get_chat_member(CHANNEL_ID, message.from_user.id)
        if member.status in ["member", "administrator", "creator"]:
            await message.answer(
                f"✅ Каналга хуш келибсиз!\n📢 {CHANNEL_URL}"
            )
        else:
            kb = InlineKeyboardBuilder()
            kb.row(InlineKeyboardButton(text="📢 Каналга аъзо бўлиш", url=CHANNEL_URL))
            await message.answer(
                "🎁 10 кун БЕПУЛ\nЭълонларни кўриш учун каналга аъзо бўлинг:",
                reply_markup=kb.as_markup()
            )
    except:
        await message.answer("❌ Канални текшириб бўлмади")

# ================== ISH BERUVCHI ==================
@dp.message(F.text == "💼 Иш берувчи")
async def employer_start(message: types.Message, state: FSMContext):
    await message.answer("🛠 Иш турини киритинг:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(EmployerStates.work_type)

@dp.message(EmployerStates.work_type)
async def step_type(message: types.Message, state: FSMContext):
    await state.update_data(work_type=message.text)
    await message.answer("📝 Иш ҳақида маълумот:")
    await state.set_state(EmployerStates.description)

@dp.message(EmployerStates.description)
async def step_desc(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("📍 Манзил:")
    await state.set_state(EmployerStates.location)

@dp.message(EmployerStates.location)
async def step_loc(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer("💰 Нархи (200 ёки келишамиз):")
    await state.set_state(EmployerStates.price)

@dp.message(EmployerStates.price)
async def step_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("⏰ Иш вақти:")
    await state.set_state(EmployerStates.work_time)

@dp.message(EmployerStates.work_time)
async def step_time(message: types.Message, state: FSMContext):
    await state.update_data(work_time=message.text)

    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📱 Контакт юбориш", request_contact=True))

    await message.answer(
        "📞 Алоқа рақамини юборинг:",
        reply_markup=kb.as_markup(resize_keyboard=True)
    )
    await state.set_state(EmployerStates.contact)

@dp.message(EmployerStates.contact)
async def step_contact(message: types.Message, state: FSMContext):

    if message.contact:
        phone = message.contact.phone_number
    elif message.text and re.match(PHONE_REGEX, message.text):
        phone = message.text
    else:
        await message.answer("❌ Рақам нотўғри")
        return

    data = await state.get_data()

    cursor.execute("""
    INSERT INTO jobs
    (employer_id, work_type, description, location, price, work_time, contact, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        message.from_user.id,
        data["work_type"],
        data["description"],
        data["location"],
        data["price"],
        data["work_time"],
        phone,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    db.commit()

    job_id = cursor.lastrowid

    await message.answer(
        f"✅ Эълонингиз сақланди\n\n"
        f"🆔 Эълон ID: {job_id}\n"
        f"💳 Тўловни админга юборинг\n\n"
        f"Админ тасдиқлаганидан кейин каналга чиқади",
        reply_markup=main_menu()
    )

    await state.clear()

# ================== ADMIN TASDIQLASH ==================
@dp.message(Command("approve"))
async def approve_job(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split()
    if len(args) != 2:
        await message.answer("Формат: /approve JOB_ID")
        return

    job_id = args[1]

    cursor.execute("SELECT * FROM jobs WHERE id = ? AND payment_status = 0", (job_id,))
    job = cursor.fetchone()

    if not job:
        await message.answer("❌ Эълон топилмади")
        return

    cursor.execute("UPDATE jobs SET payment_status = 1 WHERE id = ?", (job_id,))
    db.commit()

    text = (
        "📢 *ЯНГИ ИШ ЭЪЛОНИ*\n\n"
        f"🛠 {job[2]}\n"
        f"📝 {job[3]}\n"
        f"📍 {job[4]}\n"
        f"💰 {job[5]}\n"
        f"⏰ {job[6]}\n"
        f"📞 {job[7]}"
    )

    await bot.send_message(CHANNEL_ID, text, parse_mode="Markdown")
    await message.answer("✅ Каналга чиқарилди")

# ================== 10 KUN NAZORAT ==================
async def check_workers():
    while True:
        cursor.execute("""
        SELECT id, warned FROM users
        WHERE payment_status = 0 AND date('now') > free_until
        """)
        users = cursor.fetchall()

        for uid, warned in users:
            if warned == 0:
                await bot.send_message(
                    uid,
                    "⚠️ 10 кунлик бепул муддат тугади.\n1 кун ичида тўлов қилинг!"
                )
                cursor.execute("UPDATE users SET warned = 1 WHERE id = ?", (uid,))
                db.commit()
            else:
                await bot.ban_chat_member(CHANNEL_ID, uid)

        await asyncio.sleep(3600)

# ================== MAIN ==================
async def main():
    asyncio.create_task(check_workers())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())'''
#yangisi 2

'''import asyncio
import logging
import re
import sqlite3
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import KeyboardButton, InlineKeyboardButton

# ================== SOZLAMALAR ==================
API_TOKEN = '8361270725:AAHe4uiGMDJ998ZjffeZ94D5uu5axU8F49o'
CHANNEL_ID = -1003829181382  # Каналингиз ИД-си (албатта манфий сон)
CHANNEL_URL = "https://t.me/dayjob_khujand"

ADMIN_ID = 5971651215          # o'zingni Telegram ID

PHONE_REGEX = r"^\+?9?9?2?\d{9}$"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ================== DATABASE ==================
db = sqlite3.connect("dayjob.db")
cursor = db.cursor()

# Jadvalni yaratish (agar mavjud bo'lmasa)
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    role TEXT,
    joined_at TEXT,
    free_until TEXT,
    warned INTEGER DEFAULT 0
)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS jobs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employer_id INTEGER,
    work_type TEXT,
    description TEXT,
    location TEXT,
    price TEXT,
    work_time TEXT,
    contact TEXT,
    created_at TEXT,
    paid INTEGER DEFAULT 0
)""")
db.commit()

# ================== FSM ==================
class EmployerStates(StatesGroup):
    work_type = State()
    description = State()
    location = State()
    price = State()
    work_time = State()
    contact = State()

# ================== MENYU ==================
def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="👷‍♂️ Ишчи"),
        KeyboardButton(text="💼 Иш берувчи")
    )
    return builder.as_markup(resize_keyboard=True)

# ================== START ==================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Ассалому алайкум!\n\n"
        "👷‍♂️ Ишчи ёки 💼 Иш берувчи сифатида давом этинг:",
        reply_markup=main_menu()
    )

# ================== ISHCHI ==================
@dp.message(F.text == "👷‍♂️ Ишчи")
async def worker_handler(message: types.Message):

    # Ishchini DB ga yozish (10 kun bepul)
    cursor.execute("""
    INSERT OR IGNORE INTO users (
        id, username, full_name, role, joined_at, free_until
    ) VALUES (?, ?, ?, 'worker', ?, ?)
    """, (
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name,
        datetime.now().strftime("%Y-%m-%d"),
        (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
    ))
    db.commit()

    try:
        member = await bot.get_chat_member(CHANNEL_ID, message.from_user.id)
        if member.status in ["member", "administrator", "creator"]:
            await message.answer(
                f"✅ Сиз каналга аъзосиз.\n"
                f"📢 Эълонлар: {CHANNEL_URL}"
            )
        else:
            kb = InlineKeyboardBuilder()
            kb.row(
                InlineKeyboardButton(
                    text="📢 Каналга аъзо бўлиш",
                    url=CHANNEL_URL
                )
            )
            await message.answer(
                "❗ Эълонларни кўриш учун аввал каналга аъзо бўлинг.\n\n"
                "🎁 Сизга 10 кун БЕПУЛ!",
                reply_markup=kb.as_markup()
            )
    except:
        await message.answer("❌ Канални текшириб бўлмади.")

# ================== ISH BERUVCHI ==================
@dp.message(F.text == "💼 Иш берувчи")
async def employer_start(message: types.Message, state: FSMContext):
    await message.answer(
        "🛠 Иш турини киритинг\n"
        "(масалан: Уста / Yuk tashuvchi)",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(EmployerStates.work_type)

@dp.message(EmployerStates.work_type)
async def step_type(message: types.Message, state: FSMContext):
    await state.update_data(work_type=message.text)
    await message.answer("📝 Иш ҳақида маълумот беринг:")
    await state.set_state(EmployerStates.description)

@dp.message(EmployerStates.description)
async def step_desc(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("📍 Манзилни киритинг:")
    await state.set_state(EmployerStates.location)

@dp.message(EmployerStates.location)
async def step_loc(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer("💰 Нархи (200 ёки келишамиз):")
    await state.set_state(EmployerStates.price)

@dp.message(EmployerStates.price)
async def step_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("⏰ Иш вақти (масалан: 09:00-18:00):")
    await state.set_state(EmployerStates.work_time)

@dp.message(EmployerStates.work_time)
async def step_time(message: types.Message, state: FSMContext):
    await state.update_data(work_time=message.text)

    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text="📱 Контакт юбориш", request_contact=True))

    await message.answer(
        "📞 Алоқа рақамини юборинг\n"
        "(масалан: +992XXXXXXXX)",
        reply_markup=kb.as_markup(resize_keyboard=True)
    )
    await state.set_state(EmployerStates.contact)

# ================== CONTACT + DB ==================
@dp.message(EmployerStates.contact)
async def step_contact(message: types.Message, state: FSMContext):

    if message.contact:
        phone = message.contact.phone_number
    elif message.text and re.match(PHONE_REGEX, message.text):
        phone = message.text
    else:
        await message.answer("❌ Рақам нотўғри!")
        return

    data = await state.get_data()

    # E’lon DB ga yoziladi (hali to‘lanmagan)
    cursor.execute("""
    INSERT INTO jobs (
        employer_id, work_type, description,
        location, price, work_time,
        contact, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        message.from_user.id,
        data["work_type"],
        data["description"],
        data["location"],
        data["price"],
        data["work_time"],
        phone,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    db.commit()

    await message.answer(
        "✅ Эълонингиз сақланди.\n\n"
        "💳 Каналга чиқиши учун тўлов қилинг (admin orqali tasdiqlanadi):\n"
        "▫️ Оддий — 10 сомонӣ\n"
        "⭐ VIP — 30 сомонӣ",
        reply_markup=main_menu()
    )

    await state.clear()

# ================== ADMIN PANEL ==================
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Сиз админ эмассиз!")
        return

    cursor.execute("SELECT id, work_type, description, paid FROM jobs WHERE paid=0")
    jobs = cursor.fetchall()

    if not jobs:
        await message.answer("🎉 Ҳеч қандай to‘lov qilinmagan e’lon yo‘q.")
        return

    for job in jobs:
        job_id, work_type, desc, paid = job
        kb = InlineKeyboardBuilder()
        kb.row(
            InlineKeyboardButton(
                text="✅ To‘lov qilindi",
                callback_data=f"approve:{job_id}"
            ),
            InlineKeyboardButton(
                text="❌ Bekor qilish",
                callback_data=f"reject:{job_id}"
            )
        )
        await message.answer(
            f"🆕 E’lon ID: {job_id}\n🛠 Ish turi: {work_type}\n📝 Ma’lumot: {desc}\nTo‘lov: {paid}",
            reply_markup=kb.as_markup()
        )

# ================== CALLBACKS ==================
@dp.callback_query(F.data.startswith("approve:"))
async def approve_callback(callback: types.CallbackQuery):
    job_id = int(callback.data.split(":")[1])
    cursor.execute("UPDATE jobs SET paid=1 WHERE id=?", (job_id,))
    db.commit()

    # E’lon kanalga chiqadi
    cursor.execute("SELECT work_type, description, location, price, work_time, contact, employer_id FROM jobs WHERE id=?", (job_id,))
    job = cursor.fetchone()
    if job:
        work_type, desc, loc, price, time_, contact, emp_id = job
        cursor.execute("SELECT full_name FROM users WHERE id=?", (emp_id,))
        emp_name = cursor.fetchone()[0]
        text = (
            f"🆕 <b>ЯНГИ ЭЪЛОН!</b>\n\n"
            f"🛠 <b>Иш тури:</b> {work_type}\n"
            f"📝 <b>Маълумот:</b> {desc}\n"
            f"📍 <b>Манзил:</b> {loc}\n"
            f"💰 <b>Нархи:</b> {price}\n"
            f"⏰ <b>Иш вақти:</b> {time_}\n"
            f"📞 <b>Алоқа:</b> {contact}\n"
            f"👤 <b>Эълон берувчи:</b> {emp_name}"
        )
        await bot.send_message(CHANNEL_ID, text, parse_mode="HTML")
        await callback.message.answer("✅ E’lon kanalga chiqarildi!")

@dp.callback_query(F.data.startswith("reject:"))
async def reject_callback(callback: types.CallbackQuery):
    job_id = int(callback.data.split(":")[1])
    cursor.execute("DELETE FROM jobs WHERE id=?", (job_id,))
    db.commit()
    await callback.message.answer("❌ E’lon bekor qilindi.")

# ================== 10 KUN NAZORAT ==================
async def check_workers():
    while True:
        cursor.execute("""
        SELECT id, warned FROM users
        WHERE role='worker' AND warned=0 AND date('now') > free_until
        """)
        users = cursor.fetchall()

        for u in users:
            user_id, warned = u
            if warned == 0:
                await bot.send_message(
                    user_id,
                    "⚠️ 10 кунлик бепул муддат тугади.\n"
                    "1 кун ичида тўлов қилинг!"
                )
                cursor.execute("UPDATE users SET warned=1 WHERE id=?", (user_id,))
                db.commit()
            else:
                try:
                    await bot.ban_chat_member(CHANNEL_ID, user_id)
                except:
                    pass  # Agar bot admin bo'lmasa yoki user kanalga qo'shilmagan bo'lsa

        await asyncio.sleep(3600)  # Har soatda tekshiradi

# ================== MAIN ==================
async def main():
    asyncio.create_task(check_workers())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())'''