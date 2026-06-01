import asyncio
import sys
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiohttp import web

import database as db
import excel_generator as excel

# ⚠️ БУ ЕРГА БОТФАТҲЕРДАН ОЛГАН ҲАҚИҚИЙ ТОКЕНИНГИЗНИ ЁЗИНГ
TOKEN = "8954404679:AAGcHlXHntPNQuz3Y0-taekMrMJlGvBWQ_g"
# ⚠️ БУ ЕРГА ШАХСИЙ ТЕЛЕГРАМ ID РАҚАМИНГИЗНИ ЁЗИНГ (Қўштирноқсиз)
ADMIN_ID = 558465235  # <--- Бу ерга ўз ТЕЛЕГРАМ ID рақамингизни ёзинг!

bot = Bot(token=TOKEN)
dp = Dispatcher()

class SurveyStates(StatesGroup):
    answering = State()

class AdminStates(StatesGroup):
    waiting_for_column_name = State()
    waiting_for_full_question = State()

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

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    # Ҳар сафар /start босилганда тиқилиб қолган эски ҳолатларни мажбуран тозалаймиз
    await state.clear() 
    db.init_db()
    user_id = message.from_user.id
    
    if db.check_student_filled(user_id):
        await message.answer(
            "📋 Сиз аллақачон рўйхатдан ўтгансиз. Агар хатолик кетган бўлса, пастдаги тугма орқали қайта таҳрирлашингиз мумкин.",
            reply_markup=get_main_keyboard(True)
        )
    else:
        questions = db.get_all_questions()
        if not questions:
            await message.answer("Ҳозирча тизимда саволлар мавжуд эмас.")
            return
            
        await message.answer(
            "⚠️ **ДИҚҚАТ! ХАТОР СЎРОВНОМА!**\n\n"
            "Барча маълумотларни **ҲУЖЖАТ (Паспорт/Гувоҳнома) АСЛИДАГЕДЕК** хатосиз ёзинг!\n\n"
            f"📋 Бошланди. 1-савол:\n{questions[0][2]}",
            reply_markup=get_main_keyboard(False)
        )
        await state.update_data(current_q_index=0, questions_list=questions)
        await state.set_state(SurveyStates.answering)

@dp.message(F.text == "❌ Бекор қилиш")
async def cancel_survey(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    is_filled = db.check_student_filled(user_id)
    
    await message.answer(
        "Жараён бекор қилинди. Қайта бошлаш учун /start босинг.", 
        reply_markup=get_main_keyboard(is_filled)
    )

@dp.message(F.text == "📝 Маълумотларни таҳрирлаш")
async def edit_survey(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    db.clear_student_answers(user_id)
    questions = db.get_all_questions()
    
    await message.answer(
        "⚠️ Қайта тўлдириш бошланди. Ҳужжат аслига қараб ёзинг!\n\n"
        f"1-савол:\n{questions[0][2]}", 
        reply_markup=get_main_keyboard(False)
    )
    await state.update_data(current_q_index=0, questions_list=questions)
    await state.set_state(SurveyStates.answering)

@dp.message(F.text == "📋 Менинг маълумотларим")
async def show_my_data(message: Message):
    answers = db.get_student_answers(message.from_user.id)
    if answers:
        info = "📋 **Сиз киритган маълумотлар:**\n\n"
        for field, val in answers:
            info += f"📌 **{field}:** {val or 'Киритилмаган'}\n"
        await message.answer(info, parse_mode="Markdown")
    else:
        await message.answer("Сиз ҳали маъ

