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
ADMIN_ID = 558465235  

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
        await message.answer("Сиз ҳали маълумот киритмагансиз. /start буйруғи орқали тўлдиринг.")

@dp.message(SurveyStates.answering)
async def handle_answer(message: Message, state: FSMContext):
    if message.text in ["❌ Бекор қилиш", "📝 Маълумотларни таҳрирлаш", "📋 Менинг маълумотларим"]:
        return
        
    data = await state.get_data()
    idx = data.get('current_q_index', 0)
    q_list = data.get('questions_list', [])
    user_id = message.from_user.id
    
    if not q_list:
        await state.clear()
        return

    q_id, field_name, _ = q_list[idx]
    db.save_answer(user_id, q_id, message.text)
    
    next_idx = idx + 1
    if next_idx < len(q_list):
        await state.update_data(current_q_index=next_idx)
        await message.answer(f"📋 Кейинги савол:\n{q_list[next_idx][2]}")
    else:
        await state.clear()
        await message.answer("🎉 Раҳмат! Барча маълумотларингиз ҳужжат аслидек қабул қилинди ва базага сақланди.", reply_markup=get_main_keyboard(True))

# ================= АДМИН БУЙРУҚЛАРИ =================

@dp.message(Command("download_base"))
async def admin_download_base(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Бу буйруқ фақат тизим администратори учун очиқ!")
        return

    file_name = excel.export_students_to_excel()
    try:
        excel_file = FSInputFile(file_name, filename="Oquvchilar_Umuniy_Bazasi.csv")
        await message.answer_document(excel_file, caption="📊 База тайёр! Янги қўшилган майдонлар ҳам Excel устунларига автоматик жойлашган.")
    except Exception as e:
        await message.answer(f"Хатолик юз берди: {e}")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

@dp.message(Command("add_field"))
async def admin_add_field(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Бу буйруқ фақат тизим администратори учун очиқ!")
        return
    
    await state.clear()
    await message.answer("🆕 Янги майдон қўшиш бошланди.\n\nАввал Excel жадвалида устун номи қандай бўлишини ёзинг (Мас: Тўгарак, Касаллиги, Чет тили):")
    await state.set_state(AdminStates.waiting_for_column_name)

@dp.message(AdminStates.waiting_for_column_name)
async def admin_get_col_name(message: Message, state: FSMContext):
    await state.update_data(new_col=message.text)
    await message.answer("Энди ота-онага бериладиган тўлиқ савол матнини ёзинг (Мас: Ўқувчи дарсдан ташқари қайси тўгаракларга қатнашади?):")
    await state.set_state(AdminStates.waiting_for_full_question)

@dp.message(AdminStates.waiting_for_full_question)
async def admin_get_full_question(message: Message, state: FSMContext):
    data = await state.get_data()
    col_name = data['new_col']
    question_text = message.text
    
    db.add_new_question(col_name, question_text)
    await state.clear()
    
    user_id = message.from_user.id
    is_filled = db.check_student_filled(user_id)
    await message.answer(
        f"✅ Муваффақиятли қўшилди!\n\n📌 Excel устун номи: {col_name}\n❓ Савол матни: {question_text}\n\nЭнди янги кирган ота-оналардан бу савол ҳам автоматик равишда сўралади.",
        reply_markup=get_main_keyboard(is_filled)
    )

# ================= RENDER PORT СОЗЛАМАСИ =================
async def handle(request):
    return web.Response(text="Бот Render серверида хатосиз ишлаяпти!")

async def main():
    db.init_db()
    
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    asyncio.create_task(site.start())
    
    print(f"Веб-сервер {port}-портда ишга тушди.")
    await dp.start_polling(bot, close_bot_session=True)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
