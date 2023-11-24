from aiogram import types, Dispatcher
from bot.admin.keyboards.admin_keyboards import get_section_kb, get_store_kb, get_user_menu_kb, get_menu_admin_kb
from bot.admin.keyboards.admin_keyboards import get_edit_delete_kb, get_edit_record_kb, get_date_kb, get_in_menu_kb
from aiogram.types import ReplyKeyboardRemove
from bot.client.keyboards.user_keyboards import get_main_menu_kb
from bot.utilities.data_base import DatabaseManager
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery
from dotenv import load_dotenv
import os

load_dotenv('.env')
admin_id = os.getenv("admin_id")


# Создайте экземпляр класса DatabaseManager
db_manager = DatabaseManager()


# Класс состояний ожидания
class Waiting(StatesGroup):
    select_section = State()
    select_store = State()
    select_date = State()

    input_changes = State()


# вход в меню добавления промокода
async def edit_menu(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Для изменения/удаления записи из базы данных, "
                              "используйте фильтры для поиска необходимой записи:",
                              reply_markup=get_section_kb())
    await Waiting.select_section.set()


# получение названия раздела
async def select_section(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['section'] = msg.text
    await msg.answer("Выберите название магазина:", reply_markup=get_store_kb(msg.text))
    await Waiting.select_store.set()


# получение названия магазина
async def select_store(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['store'] = msg.text
    await msg.answer("Укажите по какую дату отфильтровать записи:", reply_markup=get_date_kb())
    await Waiting.select_date.set()


# получение даты фильтрации
async def select_date(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        p_section = data['section']
        p_store = data['store']
    results = db_manager.search_records(p_section, p_store, msg.text)
    count = len(results)
    if not results:
        await msg.answer("По заданным параметрам", reply_markup=get_in_menu_kb())
    else:
        for result in results:
            await msg.answer(f"Промо-код: <b>{result[1]}</b>\n"
                             f"Описание: <b>{result[2]}</b>\n"
                             f"ID записи: <b>{result[0]}</b>",
                             parse_mode="html",
                             reply_markup=get_edit_delete_kb(result[0]))
    await msg.answer(f"Найдено записей: <b>{count}</b>.", reply_markup=get_in_menu_kb(), parse_mode="html")
    await state.finish()


# переход в меню
async def in_menu(msg: types.Message):
    if msg.text == "Вернуться в меню пользователя":
        await msg.answer("Выберите раздел:", reply_markup=get_user_menu_kb())
    if msg.text == "Вернуться в меню администратора":
        if int(msg.from_user.id) == int(admin_id):
            await msg.answer("Выберите действие:", reply_markup=get_menu_admin_kb())
        else:
            await msg.answer("Вы не авторизованы для выполнения этой команды.", reply_markup=get_main_menu_kb())


async def cancel(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer("Действие отменено.", reply_markup=ReplyKeyboardRemove())
    if int(msg.from_user.id) == int(admin_id):
        await msg.answer("Выберите действие:", reply_markup=get_menu_admin_kb())
    else:
        await msg.answer("Вы не авторизованы для выполнения этой команды.", reply_markup=get_main_menu_kb())


# вход в редактирование записи
async def edit_record(call: CallbackQuery, state: FSMContext):
    record_id = int(call.data.split("_")[1])
    async with state.proxy() as data:
        data['record_id'] = record_id
    await call.message.edit_text("Что нужно изменить?", reply_markup=get_edit_record_kb())


# получаем объект для изменения
async def input_changes_object(call: CallbackQuery, state: FSMContext):
    change = call.data.split("_")
    async with state.proxy() as data:
        data['ch_object'] = change[1]
    await call.message.edit_text("Введите новое значение")
    await Waiting.input_changes.set()


# получаем изменения для записи
async def input_changes_record(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        record_id = data['record_id']
        ch_object = data['ch_object']
    result = db_manager.update_records(record_id, ch_object, msg.text)
    await msg.answer(result)
    await state.finish()


# отмена редактирования
async def in_admin_menu(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer("Действие отменено.", reply_markup=ReplyKeyboardRemove())
    if int(msg.from_user.id) == int(admin_id):
        await msg.answer("Выберите действие:", reply_markup=get_menu_admin_kb())
    else:
        await msg.answer("Вы не авторизованы для выполнения этой команды.", reply_markup=get_main_menu_kb())


# удаление записи
async def delete_record(call: CallbackQuery):
    record_id = int(call.data.split("_")[1])
    result = db_manager.delete_records(record_id)
    await call.message.edit_text(result)


# закрыть карточку записи
async def close_record(call: CallbackQuery):
    await call.message.delete()


def register_edit_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(edit_menu, lambda call: call.data == "edit")
    dp.register_message_handler(cancel, text="Отмена",
                                state=[Waiting.select_section, Waiting.select_store, Waiting.select_date])
    dp.register_message_handler(select_section, state=Waiting.select_section)
    dp.register_message_handler(select_store, state=Waiting.select_store)
    dp.register_message_handler(select_date, state=Waiting.select_date)
    dp.register_callback_query_handler(close_record, lambda call: call.data == "close_record")
    dp.register_callback_query_handler(delete_record, lambda call: call.data.startswith("delete_"))
    dp.register_callback_query_handler(edit_record, lambda call: call.data.startswith("change_"))
    dp.register_callback_query_handler(input_changes_object, lambda call: call.data.startswith("edit_"))
    dp.register_message_handler(input_changes_record, state=Waiting.input_changes)
    dp.register_callback_query_handler(close_record, lambda call: call.data == "close_record")
    dp.register_message_handler(in_menu, text=["Вернуться в меню администратора", "Вернуться в меню пользователя"])
