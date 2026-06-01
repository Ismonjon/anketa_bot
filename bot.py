import asyncio
import sys
import os
import re
import sqlite3
import csv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

# ⚠️ ТОКЕН ВА АДМИН ИД Рақамларингизни ёзинг
TOKEN = "8854465955:AAH_your_real_token_here"
ADMIN_ID = 123456789  

bot = Bot(token=TOKEN)
dp = Dispatcher()

DB_NAME = "web_anketa.db"  # Веб-сайт билан бир хил база номи

# Бот учун Сиз хоҳлаган аниқ устунлар кетма-кетлиги бўйича State-лар
class SurveyStates(StatesGroup):
    first_name = State()          # 1. Исми
    last_name = State()           # 2. Фамилияси
    middle_name = State()         # 3. Отасининг исми
    birthday = State()            # 4. Туғилган санаси
    birth_certificate = State()   # 5. Метрика рақами
    passport = State()            # 6. Паспорт серия
    pinfl = State()               # 7. ЖШШИР
    phone = State()               # 8. Телефон рақами
    gender = State()              # 9. Жинси
    address = State()             # 10. Яшаш манзили
    father_full_name = State()    # 11. Отасининг Ф.И.Ш (ЯНГИ)
    mother_full_name = State()    # 12. Онасининг Ф.И.Ш (ЯНГИ)
    father_work = State()         # 13. Отасининг иш жойи
    mother_work = State()         # 14. Онасининг иш жойи

# Базани бот томондан ҳам текшириб олиш функцияси
def init_bot_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id TEXT,
            first_name TEXT,
            last_name TEXT,
            middle_name TEXT,
            birthday TEXT,
            birth_certificate TEXT,
            passport TEXT,
            pinfl TEXT,
            phone TEXT,
            gender TEXT,
            address TEXT,
            father_full_name TEXT,
            mother_full_name TEXT,
            father_work TEXT,
            mother_work TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Меню тугмалари
def get_main_keyboard(is_filled):
    if is_filled:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📝 Маълумотларни таҳрирлаш")], 
                [KeyboardButton(text="📋 Менинг маълумотларим")]
            ], 
            resize_keyboard=True
        )
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Бекор қилиш")]], 
        resize_keyboard=True
    )

def get_gender_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Ўғил"), KeyboardButton(text="Қиз")],
            [KeyboardButton(text="❌ Бекор қилиш")]
        ],
        resize_keyboard=True
    )

# Базада ўқувчи бор-йўқлигини текшириш
def check_user_exists(telegram_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM responses WHERE telegram_id = ?", (str(telegram_id),))
    res = cursor.fetchone()
    conn.close()
    return res is not None

# /start буйруғи
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear() 
    init_bot_db()
    user_id = message.from_user.id
    
    if check_user_exists(user_id):
        await message.answer(
            "📋 Сиз аллақачон рўйхатдан ўтгансиз. Агар хатолик кетган бўлса, пастдаги тугма орқали қайта таҳрирлашингиз мумкин.",
            reply_markup=get_main_keyboard(True)
        )
    else:
        await message.answer(
            "⚠️ **ДИҚҚАТ! СЎРОВНОМА БОШЛАНДИ!**\n\n"
            "Барча маълумотларни **ҲУЖЖАТ АСЛИДАГИДЕК** ва сўралган форматда хатосиз ёзинг!\n\n"
            "📋 **1-савол:** Ўқувчининг исмини киритинг:",
            reply_markup=get_main_keyboard(False)
        )
        await state.set_state(SurveyStates.first_name)

# Бекор қилиш тугмаси
@dp.message(F.text == "❌ Бекор қилиш")
async def cancel_survey(message: Message, state: FSMContext):
    await state.clear()
    is_filled = check_user_exists(message.from_user.id)
    await message.answer(
        "Жараён бекор қилинди. Қайта бошлаш учун /start босинг.", 
        reply_markup=get_main_keyboard(is_filled)
    )

# Таҳрирлаш (Эскисини ўчириб янгидан бошлаш)
@dp.message(F.text == "📝 Маълумотларни таҳрирлаш")
async def edit_survey(message: Message, state: FSMContext):
    await state.clear()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM responses WHERE telegram_id = ?", (str(message.from_user.id),))
    conn.commit()
    conn.close()
    
    await message.answer(
        "⚠️ Қайта тўлдириш бошланди. Ҳужжат аслига қараб ёзинг!\n\n"
        "📋 **1-савол:** Ўқувчининг исмини киритинг:",
