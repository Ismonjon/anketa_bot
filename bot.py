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

TOKEN = "8954404679:AAGcHlXHntPNQuz3Y0-taekMrMJlGvBWQ_g"

bot = Bot(token=TOKEN)
dp = Dispatcher()

class StudentForm(StatesGroup):
    waiting_for_firstname = State()
    waiting_for_lastname = State()
    waiting_for_middlename = State()
    waiting_for_birthdate = State()
    waiting_for_certificate = State()
    waiting_for_passport = State()
    waiting_for_pinfl = State()
    waiting_for_phone = State()
    waiting_for_gender = State()
    waiting_for_address = State()
    waiting_for_father = State()
    waiting_for_mother = State()
    waiting_for_work = State()

def get_gender_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Ўғил бола"), KeyboardButton(text="Қиз бола")]],
        resize_keyboard=True, one_time_keyboard=True
    )

def get_edit_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📝 Маълумотларни таҳрирлаш")], [KeyboardButton(text="📋 Менинг маълумотларим")]],
        resize_keyboard=True
    )

def get_cancel_keyboard():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ Бекор қилиш")]], resize_keyboard=True)

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    db.init_db()
    user_id = message.from_user.id
    student = db.get_student(user_id)
    
    if student:
        await message.answer(
            "📋 Сиз аллақачон рўйхатдан ўтгансиз ва маълумотларингиз базага қўшилган.\n"
            "Агар хатолик кетган бўлса, пастдаги тугма орқали уларни қайта таҳрирлашингиз мумкин.",
            reply_markup=get_edit_keyboard()
        )
    else:
        # Энг биринчи огоҳлантириш матни шу ерда
        await message.answer(
            "⚠️ **ДИҚҚАТ! ХАТОР СЎРОВНОМА!**\n\n"
            "Алоҳида илтимос: Барча маълумотларни **Ўқувчининг ҲУЖЖАТИ (Паспорт ёки Туғилганлик ҳақида гувоҳнома) АСЛИДАГЕДЕК**, ҳеч қандай хатосиз ва қисқартиришсиз ёзишингизни сўраймиз!\n\n"
            "📋 Бўлим: Ўқувчининг ИСМИНИ киритинг (ҳужжатдагидек):",
            reply_markup=get_cancel_keyboard(),
            parse_mode="Markdown"
        )
        await state.set_state(StudentForm.waiting_for_firstname)

@dp.message(F.text == "❌ Бекор қилиш")
async def cancel_fill(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    student = db.get_student(user_id)
    if student:
        await message.answer("Жараён бекор қилинди.", reply_markup=get_edit_keyboard())
    else:
        await message.answer("Жараён бекор қилинди. Қайта бошлаш учун /start босинг.", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="/start")]], resize_keyboard=True))

@dp.message(F.text == "📝 Маълумотларни таҳрирлаш")
async def edit_profile(message: Message, state: FSMContext):
    await message.answer(
        "⚠️ Қайта рўйхатдан ўтиш бошланди. Илтимос, маълумотларни ҳужжат аслидек киритинг!\n\n"
        "Ўқувчининг ИСМИНИ киритинг:", 
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(StudentForm.waiting_for_firstname)

@dp.message(F.text == "📋 Менинг маълумотларим")
async def show_my_data(message: Message):
    student = db.get_student(message.from_user.id)
    if student:
        info = (
            f"👤 **Ўқувчи:** {student[2]} {student[1]} {student[3]}\n"
            f"📅 **Тўғилган сана:** {student[4]}\n"
            f"📜 **Метрика рақами:** {student[5]}\n"
            f"🪪 **Паспорт:** {student[6]}\n"
            f"🔢 **ЖШШИР (ПИНФЛ):** {student[7]}\n"
            f"📞 **Телефон:** {student[8]}\n"
            f"⚧ **Жинси:** {student[9]}\n"
            f"📍 **Манзил:** {student[10]}\n"
            f"👨‍👦 **Отаси:** {student[11]}\n"
            f"👩‍👦 **Онаси:** {student[12]}\n"
            f"💼 **Иш жойлари:** {student[13]}"
        )
        await message.answer(info, parse_mode="Markdown", reply_markup=get_edit_keyboard())

# --- САВОЛЛАРДА ҲУЖЖАТ ТАЛАБИ ЭСЛАТИЛДИ ---

@dp.message(StudentForm.waiting_for_firstname)
async def process_firstname(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await message.answer("Ўқувчининг ФАМИЛИЯСИНИ киритинг (ҳужжатдагидек):")
    await state.set_state(StudentForm.waiting_for_lastname)

@dp.message(StudentForm.waiting_for_lastname)
async def process_lastname(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await message.answer("Ўқувчининг ОТАСИНИНГ ИСМИНИ киритинг (ҳужжатдагидек):")
    await state.set_state(StudentForm.waiting_for_middlename)

@dp.message(StudentForm.waiting_for_middlename)
async def process_middlename(message: Message, state: FSMContext):
    await state.update_data(middle_name=message.text)
    await message.answer("Тўғилган куни, ойи ва йилини киритинг (гувоҳномадагидек, мас: 15.08.2012):")
    await state.set_state(StudentForm.waiting_for_birthdate)

@dp.message(StudentForm.waiting_for_birthdate)
async def process_birthdate(message: Message, state: FSMContext):
    await state.update_data(birth_date=message.text)
    await message.answer("Туг`илганлик ҳақида гувоҳнома (метрика) серияси ва рақамини аниқ ёзинг:")
    await state.set_state(StudentForm.waiting_for_certificate)

@dp.message(StudentForm.waiting_for_certificate)
async def process_certificate(message: Message, state: FSMContext):
    await state.update_data(birth_certificate=message.text)
    await message.answer("Агар паспорти (ИД-картаси) бўлса, серия ва рақамини ёзинг (Бўлмаса 'Йўқ' деб ёзинг):")
    await state.set_state(StudentForm.waiting_for_passport)

@dp.message(StudentForm.waiting_for_passport)
async def process_passport(message: Message, state: FSMContext):
    await state.update_data(passport=message.text)
    await message.answer("Ўқувчи ёки ота-онанинг ЖШШИР (паспорт пастидаги 14 хонали ПИНФЛ) кодини аниқ киритинг:")
    await state.set_state(StudentForm.waiting_for_pinfl)

@dp.message(StudentForm.waiting_for_pinfl)
async def process_pinfl(message: Message, state: FSMContext):
    clean_text = message.text.replace(" ", "")
    if len(clean_text) < 7:
        await message.answer("Илтимос, ЖШШИР кодини тўғри киритинг:")
        return
    await state.update_data(pinfl=clean_text)
    await message.answer("Алоқа учун ишлайдиган телефон рақамини киритинг (Мас: +998901234567):")
    await state.set_state(StudentForm.waiting_for_phone)

@dp.message(StudentForm.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Ўқувчининг жинсини танланг:", reply_markup=get_gender_keyboard())
    await state.set_state(StudentForm.waiting_for_gender)

@dp.message(StudentForm.waiting_for_gender)
async def process_gender(message: Message, state: FSMContext):
    if message.text not in ["Ўғил бола", "Қиз бола"]:
        await message.answer("Илтимос, қуйидаги тугмалардан бирини танланг:", reply_markup=get_gender_keyboard())
        return
    await state.update_data(gender=message.text)
    await message.answer("Паспортдаги рўйхатда турган (прописка) тўлиқ манзилини киритинг:", reply_markup=get_cancel_keyboard())
    await state.set_state(StudentForm.waiting_for_address)

@dp.message(StudentForm.waiting_for_address)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("Отасининг тўлиқ исми, фамилияси ва шарифини киритинг (паспортдагидек):")
    await state.set_state(StudentForm.waiting_for_father)

@dp.message(StudentForm.waiting_for_father)
async def process_father(message: Message, state: FSMContext):
    await state.update_data(father_name=message.text)
    await message.answer("Онасининг тўлиқ исми, фамилияси ва шарифини киритинг (паспортдагидек):")
    await state.set_state(StudentForm.waiting_for_mother)

@dp.message(StudentForm.waiting_for_mother)
async def process_mother(message: Message, state: FSMContext):
    await state.update_data(mother_name=message.text)
    await message.answer("Ота-онасининг расмий иш жойи ва лавозимини киритинг (Мас: 4-мактабда ўқитувчи, нафақада, вақтинча ишсиз ва ҳ.к.):")
    await state.set_state(StudentForm.waiting_for_work)

@dp.message(StudentForm.waiting_for_work)
async def process_work(message: Message, state: FSMContext):
    await state.update_data(parents_work=message.text)
    user_data = await state.get_data()
    user_id = message.from_user.id
    
    existing_student = db.get_student(user_id)
    if existing_student:
        db.update_student(user_id, user_data)
        await message.answer("✅ Маълумотларингиз ҳужжат асосида муваффақиятли янгиланди!", reply_markup=get_edit_keyboard())
    else:
        db.save_student(user_id, user_data)
        await message.answer("🎉 Раҳмат! Маълумотларингиз ҳужжат аслидек қабул қилинди ва базага хавфсиз сақланди.", reply_markup=get_edit_keyboard())
        
    await state.clear()

# --- АДМИН УЧУН ЭКСПОРТ БУЙРУҚИ ---
@dp.message(Command("download_base"))
async def admin_download_base(message: Message):
    # ХАВФСИЗЛИК ЧЕКЛОВИ: Ўз ID рақамингизни шу ерга ёзинг (Мас: ADMIN_ID = 512345678)
    ADMIN_ID = 123456789  
    
    if message.from_user.id != ADMIN_ID and ADMIN_ID != 123456789:
        await message.answer("❌ Бу буйруқ фақат тизим администратори учун очиқ!")
        return

    file_name = excel.export_students_to_excel()
    try:
        excel_file = FSInputFile(file_name, filename="Oquvchilar_Умумий_Базаси.csv")
        await message.answer_document(excel_file, caption="📊 Жадвал тайёр! Барча ўқувчилар рўйхати ҳужжат асосида Excel файлида жойлашган.")
    except Exception as e:
        await message.answer(f"Хатолик юз берди: {e}")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

async def main():
    db.init_db()
    
    async def handle(request):
        return web.Response(text="Students DB Bot is running perfectly!")
        
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000)))
    asyncio.create_task(site.start())
    
    await dp.start_polling(bot, close_bot_session=True)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
