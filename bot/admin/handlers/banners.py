from aiogram import types, Dispatcher
from bot.admin.keyboards.admin_keyboards import get_menu_admin_kb
from bot.admin.keyboards.banners_kb import get_menu_banners_kb, get_store_kb, get_section_kb
from bot.utilities.data_base import DatabaseManager
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery


# Создайте экземпляр класса DatabaseManager
db_manager = DatabaseManager()


# Класс состояний ожидания
class Waiting(StatesGroup):
    image = State()


# вход в управление баннерами
async def banners_control(call: CallbackQuery):
    await call.message.edit_text("Изменить баннер для", reply_markup=get_menu_banners_kb())


# управление баннерами разделов
async def control_for_section(call: CallbackQuery):
    await call.message.edit_text("Изменить баннер для раздела", reply_markup=get_section_kb())


# управление баннерами магазинов
async def control_for_store(call: CallbackQuery):
    await call.message.edit_text("Изменить баннер для магазина", reply_markup=get_store_kb())


# управление дефолтными баннерами
async def control_for_default(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['banner_for'] = "Default"
    await call.message.edit_text("Отправьте баннер, который будет использоваться по-умолчанию:")
    await Waiting.image.set()


# получаем объект для загрузки баннера
async def banner_for_change(call: CallbackQuery, state: FSMContext):
    banner_for = call.data.split("_")[1]
    async with state.proxy() as data:
        data['banner_for'] = banner_for
    await call.message.edit_text("Отправьте баннер:")
    await Waiting.image.set()


# получаем баннер
async def banner_image(msg: types.Message, state: FSMContext):

    photo = msg.photo[-1]
    file_id = photo.file_id

    async with state.proxy() as data:
        banner_for = data['banner_for']
    result = db_manager.update_banners(file_id, banner_for)
    await msg.answer(result, parse_mode="html", reply_markup=get_menu_banners_kb())
    await state.finish()


# вернуться в меню админа
async def in_main_menu(call: CallbackQuery):
    await call.message.edit_text("Добро пожаловать в панель управления", reply_markup=get_menu_admin_kb())


# вернуться в меню баннеров
async def in_banners_menu(call: CallbackQuery):
    await call.message.edit_text("Изменить баннер для", reply_markup=get_menu_banners_kb())


def register_banners_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(banners_control, lambda call: call.data == "banners")
    dp.register_callback_query_handler(control_for_section, lambda call: call.data == "for_section")
    dp.register_callback_query_handler(control_for_store, lambda call: call.data == "for_store")
    dp.register_callback_query_handler(control_for_default, lambda call: call.data == "default")
    dp.register_callback_query_handler(banner_for_change, lambda call: call.data.startswith("chbanner_"))
    dp.register_message_handler(banner_image, content_types=[types.ContentType.PHOTO], state=Waiting.image)
    dp.register_callback_query_handler(in_main_menu, lambda call: call.data == "back_in_main")
    dp.register_callback_query_handler(in_banners_menu, lambda call: call.data == "back_in_menu_banners")
