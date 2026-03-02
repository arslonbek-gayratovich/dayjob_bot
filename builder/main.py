import asyncio
import logging
import re
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

API_TOKEN = "8361270725:AAH6Pc1d5UnrGaxvIi1e_ITBJhBPYdu_4aI"
CHANNEL_ID = -1003829181382
CHANNEL_URL = "https://t.me/dayjob_khujand/19"

PHONE_REGEX = r"^\d{9}$"
DATE_REGEX = r"^\d{2}\.\d{2}\.\d{4}$"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ====== REGIONLAR ======
MAIN_LOCATIONS = ["Душанбе", "Хуҷанд", "Бохтар", "Кӯлоб", "Хоруғ", "Истаравшан"]
OTHER_LOCATIONS = [
    "Ваҳдат","Ҳисор","Шаҳринав","Варзоб","Рӯдакӣ","Бӯстон","Гулистон",
    "Исфара","Конибодом","Панҷакент","Ашт","Спитамен","Зафаробод",
    "Норак","Ёвон","Вахш","Данғара","Фархор","Ҳамадонӣ","Ҷайҳун",
    "Қубодиён","Муъминобод","Рашт","Тоҷикобод","Лахш","Нуробод"
]

# ====== FSM ======
class EmployerStates(StatesGroup):
    date = State()
    date_manual = State()
    work_time = State()
    work_type = State()
    description = State()
    location_main = State()
    location_other = State()
    location_extra = State()
    price = State()
    name = State()
    contact = State()
    preview = State()
    edit_field = State()

# ====== KEYBOARDS ======
def main_menu():
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(text="👷‍♂️ Коргар", callback_data="role_worker"),
        types.InlineKeyboardButton(text="💼 Кордиҳанда", callback_data="role_employer")
    )
    return kb.as_markup()

def main_locations_kb():
    kb = InlineKeyboardBuilder()
    for loc in MAIN_LOCATIONS:
        kb.button(text=loc, callback_data=f"loc_{loc}")
    kb.button(text="🏙 Дигар шаҳру ноҳияҳо", callback_data="loc_other")
    kb.adjust(2)
    return kb.as_markup()

def other_locations_kb():
    kb = InlineKeyboardBuilder()
    for loc in OTHER_LOCATIONS:
        kb.button(text=loc, callback_data=f"loc_{loc}")
    kb.adjust(2)
    return kb.as_markup()

def price_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="💬 Дар сӯҳбат", callback_data="price_chat")
    return kb.as_markup()

# ====== START ======
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "<b>🤝 Dayjob — платформа барои пайваст кардани коргар ва кордиҳанда</b>\n\nЛутфан интихоб кунед!",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "role_worker")
async def worker_handler(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(
            text="📢 Дидани зълонҳо дар канал",
            url=CHANNEL_URL
        )
    )

    await callback.message.answer(
        "👷‍♂️ <b>Эълонҳо барои коргарон</b>\n\n"
        "Тавассути тугмаи зерин ба канал гузашта, "
        "метавонед кори худро ёбед. 👇",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

# ====== EMPLOYER FLOW ======
@dp.callback_query(F.data == "role_employer")
async def employer_start(callback: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(text="Имрӯз", callback_data="date_today"),
        types.InlineKeyboardButton(text="Пагоҳ", callback_data="date_tomorrow"),
        types.InlineKeyboardButton(text="Дигар рӯз", callback_data="date_other")
    )
    await callback.message.answer("📅 Санаи кор:", reply_markup=kb.as_markup())
    await state.set_state(EmployerStates.date)
    await callback.answer()

@dp.callback_query(EmployerStates.date)
async def step_date(callback: types.CallbackQuery, state: FSMContext):
    today = datetime.now()
    if callback.data == "date_today":
        date = today.strftime("%d.%m.%Y")
    elif callback.data == "date_tomorrow":
        date = (today + timedelta(days=1)).strftime("%d.%m.%Y")
    else:
        await callback.message.answer("📅 Санаро ворид кунед: Мисол:25.02.2026")
        await state.set_state(EmployerStates.date_manual)
        await callback.answer()
        return

    await state.update_data(date=date)
    await callback.message.answer("⏰ Соати кор: Мисол: 09:00–18:00 ⏰, 08:00–14:00 🌅 ё дар асоси ҳаҷм(Объём)🕊")
    await state.set_state(EmployerStates.work_time)
    await callback.answer()

@dp.message(EmployerStates.date_manual)
async def manual_date(message: types.Message, state: FSMContext):
    if not re.match(DATE_REGEX, message.text):
        await message.answer("❌ Формат нодуруст (25.02.2026)")
        return
    await state.update_data(date=message.text)
    await message.answer("⏰ Соати кор:Мисол: 09:00–18:00 ⏰, 08:00–14:00 🌅, ё дар асоси ҳаҷм(Объём) 🕊")
    await state.set_state(EmployerStates.work_time)

@dp.message(EmployerStates.work_time)
async def step_time(message: types.Message, state: FSMContext):
    await state.update_data(work_time=message.text)
    await message.answer("🛠 Намуди кор:Мисол: Усто,Электрик,боркаш 🚚")
    await state.set_state(EmployerStates.work_type)

@dp.message(EmployerStates.work_type)
async def step_type(message: types.Message, state: FSMContext):
    await state.update_data(work_type=message.text)
    await message.answer("📝 Тавсифи кӯтоҳ дар бораи кор:Мисол: Таъмири хонаи 2 ҳуҷра 🌷, аз мошин бор фуровардaн лозим 🚚")
    await state.set_state(EmployerStates.description)

@dp.message(EmployerStates.description)
async def step_desc(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("📍 Шаҳр ё ноҳия:", reply_markup=main_locations_kb())
    await state.set_state(EmployerStates.location_main)

@dp.callback_query(EmployerStates.location_main)
async def location_main(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "loc_other":
        await callback.message.answer("🏙 Интихоб кунед:", reply_markup=other_locations_kb())
        await state.set_state(EmployerStates.location_other)
    else:
        await state.update_data(location_main=callback.data.replace("loc_", ""))
        await callback.message.answer("➕ Қисми иловагӣ: Мисол: кӯчаи Сомонӣ,14🌿")
        await state.set_state(EmployerStates.location_extra)
    await callback.answer()

@dp.callback_query(EmployerStates.location_other)
async def location_other(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(location_main=callback.data.replace("loc_", ""))
    await callback.message.answer("➕ Қисми иловагӣ:  Мисол: кӯчаи Сомонӣ,14🌿")
    await state.set_state(EmployerStates.location_extra)
    await callback.answer()

@dp.message(EmployerStates.location_extra)
async def location_extra(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(location=f"{data['location_main']}, {message.text}")
    await message.answer(
        "💰 Музди меҳнат: Мисол: 250 сомонӣ 💰 ё дар суҳбат 🤝:",
        reply_markup=price_kb()
    )
    await state.set_state(EmployerStates.price)

@dp.callback_query(F.data == "price_chat", EmployerStates.price)
async def price_chat(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(price="Дар сӯҳбат")
    await callback.message.answer("👤 Ном: Мисол: Али 🌸")
    await state.set_state(EmployerStates.name)
    await callback.answer()

@dp.message(EmployerStates.price)
async def step_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer("👤 Ном:  Мисол: Али 🌸")
    await state.set_state(EmployerStates.name)

@dp.message(EmployerStates.name)
async def step_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📞 Телефон: Мисол: 987654321 📞")
    await state.set_state(EmployerStates.contact)

@dp.message(EmployerStates.contact)
async def step_contact(message: types.Message, state: FSMContext):
    if not re.match(PHONE_REGEX, message.text):
        await message.answer("❌ Рақам нодуруст: Мисол: 987654321 📞")
        return
    await state.update_data(contact=message.text)
    await send_preview(message, state)

# ====== PREVIEW + EDIT ======
async def send_preview(message: types.Message, state: FSMContext):
    d = await state.get_data()
    text = (

        f"🆕 <b>ЭЪЛОНИ НАВ</b>\n\n"
        f"🛠 <b>Намуди кор:</b> {d['work_type']}\n"
        f"📝 <b>Маълумоти иловагӣ:</b>\n{d['description']}\n"
        f"📅 <b>Рӯзи иҷрои кор:</b> {d['date']}\n"
        f"⏰ <b>Соати кор:</b> {d['work_time']}\n"
        f"📍 <b>Макони кор:</b> {d['location']}\n"
        f"💵 <b>Маош:</b> {d['price']}\n"
        f"👤 <b>Номи корфармо:</b> {d['name']}\n"
        f"📞 <b>Барои тамос:</b> {d['contact']}\n"
        f"✨ Кор ҳаст — даромад ҳаст!.\n🔥 Барори кор"

        )
    kb = InlineKeyboardBuilder()
    kb.row(
        types.InlineKeyboardButton(text="✅ Дуруст", callback_data="confirm"),
        types.InlineKeyboardButton(text="✏️ Таҳрир", callback_data="edit")
    )
    kb.row(types.InlineKeyboardButton(text="❌ Бекор кардан", callback_data="cancel"))
    await message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await state.set_state(EmployerStates.preview)

@dp.callback_query(F.data == "edit", EmployerStates.preview)
async def edit_menu(callback: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardBuilder()
    for f in ["Сана","Вақт","Намуди кор","Тавсиф","Суроға","Музди меҳнат","Ном","Телефон"]:
        kb.button(text=f, callback_data=f"edit_{f}")
    kb.adjust(2)
    await callback.message.answer("✏️ Кадом қисмро тағйир додан мехоҳед?", reply_markup=kb.as_markup())
    await state.set_state(EmployerStates.edit_field)
    await callback.answer()

@dp.callback_query(F.data.startswith("edit_"), EmployerStates.edit_field)
async def choose_edit(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(editing=callback.data.replace("edit_", ""))
    await callback.message.answer("✏️ Маълумоти нав:")
    await callback.answer()

@dp.message(EmployerStates.edit_field)
async def save_edit(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data({data["editing"]: message.text})
    await send_preview(message, state)

from aiogram import types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder

@dp.callback_query(F.data == "confirm", EmployerStates.preview)
async def confirm(callback: types.CallbackQuery, state: FSMContext):
    # 1️⃣ E'lonni kanalga joylash
    await bot.send_message(
        CHANNEL_ID,
        callback.message.html_text,
        parse_mode="HTML"
    )

    # 2️⃣ Tugmalarni SHU YERDA yaratamiz
    kb = InlineKeyboardBuilder()
    kb.button(
        text="📢 Дидани эълон дар канал",
        url=CHANNEL_URL
    )

    kb.adjust(1)

    kb.button(
        text="🔄 Аз нав оғоз кардан",
        callback_data="restart"
    )
    kb.adjust(1)

    # 3️⃣ Foydalanuvchiga javob
    user_name = callback.from_user.first_name or "Мӯҳтарам корфармо"

    await callback.message.answer(
        f"✅ <b>Эълон бо муваффақият ҷойгир карда шуд!</b>\n\n"
        f"🤍 Ташаккур, <b>{user_name}</b>!\n"
        f"🌷 Мо эълони шуморо бо камоли эҳтиром омода кардем "
        f"ва ба корҷӯён пешкаш намудем 🌿",
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )



    @dp.callback_query(F.data == "restart")
    async def restart(callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        await callback.message.answer("🔁 Аз нав оғоз мекунем")
        await start_handler(callback.message)
        await callback.answer()

    # 4️⃣ State tozalash
    await state.clear()
    await callback.answer()
@dp.callback_query(F.data == "cancel", EmployerStates.preview)
async def cancel(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Бекор қарда шуд")
    await state.clear()
    await start_handler(callback.message)
    await callback.answer()




# ====== MAIN ======
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
