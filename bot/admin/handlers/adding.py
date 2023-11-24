from aiogram import types, Dispatcher
from bot.admin.keyboards.admin_keyboards import get_section_kb, get_store_kb, get_cancel_kb, get_menu_admin_kb
from aiogram.types import ReplyKeyboardRemove
from bot.client.keyboards.user_keyboards import get_main_menu_kb
from bot.utilities.data_base import DatabaseManager
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery
import asyncio
from aiogram import exceptions
from dotenv import load_dotenv
import os

load_dotenv('.env')
admin_id = os.getenv("admin_id")

# Создайте экземпляр класса DatabaseManager
db_manager = DatabaseManager()


# Класс состояний ожидания
class Waiting(StatesGroup):
    add_section = State()
    add_store = State()
    add_code = State()
    add_description = State()
    add_date = State()

    edit_section = State()
    edit_store = State()
    edit_code = State()
    edit_description = State()
    edit_date = State()


# вход в меню добавления промокода
async def adding_menu(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Введите название раздела:", reply_markup=get_section_kb())
    await Waiting.add_section.set()


# получение названия раздела
async def add_section(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['section'] = msg.text
    await msg.answer("Введите название магазина:", reply_markup=get_store_kb(msg.text))
    await Waiting.add_store.set()


# получение названия магазина
async def add_store(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['store'] = msg.text
    await msg.answer("Введите промокод:", reply_markup=get_cancel_kb())
    await Waiting.add_code.set()


# получение промокода
async def add_code(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['code'] = msg.text
    await msg.answer("Введите описание промокода:", reply_markup=get_cancel_kb())
    await Waiting.add_description.set()


# получение описания промокода
async def add_description(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = msg.text
    await msg.answer("Введите дату, по которую промокод будет активен:", reply_markup=get_cancel_kb())
    await Waiting.add_date.set()


# получение даты промокода
async def add_date(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        p_section = data['section']
        p_store = data['store']
        p_code = data['code']
        p_description = data['description']
    result = db_manager.add_new_codes(p_section, p_store, p_code, p_description, msg.text)
    await msg.answer(result, reply_markup=get_menu_admin_kb())
    await state.finish()


async def cancel(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer("Действие отменено.", reply_markup=ReplyKeyboardRemove())
    if int(msg.from_user.id) == int(admin_id):
        await msg.answer("Выберите действие:", reply_markup=get_menu_admin_kb())
    else:
        await msg.answer("Вы не авторизованы для выполнения этой команды.", reply_markup=get_main_menu_kb())


def register_adding_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(adding_menu, lambda call: call.data == "adding")
    dp.register_message_handler(cancel, text="Отмена",
                                state=[Waiting.add_section, Waiting.add_store, Waiting.add_code,
                                       Waiting.add_description, Waiting.add_date])
    dp.register_message_handler(add_section, state=Waiting.add_section)
    dp.register_message_handler(add_store, state=Waiting.add_store)
    dp.register_message_handler(add_code, state=Waiting.add_code)
    dp.register_message_handler(add_description, state=Waiting.add_description)
    dp.register_message_handler(add_date, state=Waiting.add_date)
