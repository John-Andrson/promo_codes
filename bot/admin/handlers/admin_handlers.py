from aiogram import types, Dispatcher
from bot.admin.keyboards.admin_keyboards import get_menu_admin_kb, get_all_users_kb, get_cancel_sending_kb
from bot.admin.keyboards.admin_keyboards import get_start_sending_kb, get_user_menu_kb
from bot.client.keyboards.user_keyboards import get_main_menu_kb
from bot.utilities.data_base import DatabaseManager
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery
import asyncio
from aiogram import exceptions
from dotenv import load_dotenv
import os


# Создайте экземпляр класса DatabaseManager
db_manager = DatabaseManager()


# Класс состояний ожидания
class Waiting(StatesGroup):
    input_id_users = State()
    input_msg_text = State()
    input_cmd_send = State()


load_dotenv('.env')
admin_id = os.getenv("admin_id")


# вход в меню админа
async def cmd_admin(msg: types.Message):
    if int(msg.from_user.id) == int(admin_id):
        await msg.answer("Добро пожаловать в панель управления", reply_markup=get_menu_admin_kb())
    else:
        await msg.answer("Вы не авторизованы для выполнения этой команды.", reply_markup=get_user_menu_kb())


# вход в меню рассылки
async def sending_menu(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Введите ID пользователя или ID пользователей через запятую",
                              reply_markup=get_all_users_kb())
    await Waiting.input_id_users.set()


# id всех пользователей из БД
async def send_all(msg: types.Message, state: FSMContext):
    results = db_manager.search_user_ids()
    ids = [user_id[0] for user_id in results]
    async with state.proxy() as data:
        data['ids'] = ids
    await msg.answer("Введите текс сообщения для рассылки:", reply_markup=get_cancel_sending_kb())
    await Waiting.input_msg_text.set()


# получаем id пользователей для рассылки
async def input_ids(msg: types.Message, state: FSMContext):
    parts = [part.strip() for part in msg.text.split(',')]
    # проверяем, состоит ли каждая часть только из цифр
    for part in parts:
        if not part.isdigit():
            # если хотя бы одна часть не является числом, отправляем сообщение и выходим
            await msg.answer("Я вас не понимаю. Введите пожалуйста еще раз ID."
                             "Если у вас более одного ID, то разделите их запятой")
            return
    # записываем во временное хранилище
    ids = [int(part) for part in parts]
    async with state.proxy() as data:
        data['ids'] = ids
    await msg.answer("Введите текс сообщения для рассылки:", reply_markup=get_cancel_sending_kb())
    await Waiting.input_msg_text.set()


# получаем текс для рассылки
async def input_text(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['s_text'] = msg.text
    await msg.answer("Все готово. Нажмите <b>Начать рассылку</b>, чтобы отправить сообщение.",
                     parse_mode="html",
                     reply_markup=get_start_sending_kb())
    await Waiting.input_cmd_send.set()


# отправка сообщений
async def start_sending_msg(msg: types.Message, state: FSMContext):
    import main
    await msg.answer("Рассылка запущена.", reply_markup=get_menu_admin_kb())
    async with state.proxy() as data:
        ids = data['ids']
        s_text = data['s_text']

    for item in ids:
        try:
            await main.bot.send_message(chat_id=item, text=s_text)
            await asyncio.sleep(1)
        except exceptions.ChatNotFound as chat_not_found_error:
            error = f"Ошибка: Чат {item} не найден. Данное сообщение не было отправлено."
            await main.bot.send_message(chat_id=admin_id, text=error)

    await state.finish()


# назад в меню админа
async def back_in__menu_admin(msg: types.Message, state: FSMContext):
    await state.finish()
    if int(msg.from_user.id) == int(admin_id):
        await msg.answer("Выберите действие:", reply_markup=get_menu_admin_kb())
    else:
        await msg.answer("Вы не авторизованы для выполнения этой команды.", reply_markup=get_main_menu_kb())


# выгрузка ID пользователей
async def save_id(call: CallbackQuery):
    await call.message.delete()
    import main

    results = db_manager.search_user_ids()
    with open('id_users.txt', 'w') as file:
        for item in results:
            file.write(str(item[0]) + '\n')
    await main.bot.send_document(chat_id=admin_id, document=open('id_users.txt', 'rb'),
                                 reply_markup=get_main_menu_kb())
    await call.message.answer("☝️☝️☝️☝️☝️", reply_markup=get_menu_admin_kb())


# выход из меню админа
async def close_menu_admin(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Чтобы вернуться в меню администратора, введите команду /admin.\n"
                              "Чтобы найти промокод, перейдите в меню выбора разделов.",
                              reply_markup=get_user_menu_kb())


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(cmd_admin, commands=['admin'])
    dp.register_callback_query_handler(close_menu_admin, lambda call: call.data == "close")
    dp.register_callback_query_handler(sending_menu, lambda call: call.data == "sending")
    dp.register_message_handler(back_in__menu_admin, text="🔙 Вернуться в меню администратора",
                                state=[Waiting.input_id_users, Waiting.input_msg_text, Waiting.input_cmd_send])
    dp.register_message_handler(send_all, text="Отправить всем", state=Waiting.input_id_users)
    dp.register_message_handler(input_ids, state=Waiting.input_id_users)
    dp.register_message_handler(input_text, state=Waiting.input_msg_text)
    dp.register_message_handler(start_sending_msg, text="Начать рассылку", state=Waiting.input_cmd_send)
    dp.register_callback_query_handler(save_id, lambda call: call.data == "download")
