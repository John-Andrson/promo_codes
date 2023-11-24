from aiogram import types, Dispatcher
from bot.client.keyboards.user_keyboards import get_section_kb, get_store_kb, get_main_menu_kb
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from bot.utilities.data_base import DatabaseManager
from aiogram.types import ReplyKeyboardRemove


# Создайте экземпляр класса DatabaseManager
db_manager = DatabaseManager()


async def cmd_start(msg: types.Message) -> None:
    db_manager.add_users(msg.from_user.id, msg.from_user.first_name, f"@{msg.from_user.username}")
    result = db_manager.search_banner_id("Default")
    import main

    des_text = "Привет, я - <b>Название бота</b>!\n" \
               "Я помогу тебе сделать покупки в интернете еще более приятными. " \
               "Что может быть лучше чем дополнительная скидка при покупке, не так ли?\n" \
               "Я постараюсь найти для тебя промокод, выбери раздел:"

    await main.bot.send_photo(msg.chat.id, photo=result[0], caption=des_text, parse_mode="html",
                              reply_markup=get_section_kb())


async def search_promo(msg: types.Message) -> None:
    import main
    new_caption = "Я постараюсь найти для тебя промокод, выбери раздел:"
    result = db_manager.search_banner_id("Default")
    await main.bot.send_photo(msg.chat.id, photo=result[0], caption=new_caption, reply_markup=get_section_kb())


async def back_to_section(msg: types.Message, state: FSMContext) -> None:
    await msg.answer("Давай выберем магазин:", reply_markup=ReplyKeyboardRemove())
    import main
    async with state.proxy() as data:
        section = data['section']
    result = db_manager.search_banner_id(section)
    await main.bot.send_photo(msg.chat.id, result[0], reply_markup=get_store_kb(section))


async def enter_to_section(call: CallbackQuery, state: FSMContext):
    data = call.data.split("_")
    section = data[1]  # Получаем выбранный раздел
    async with state.proxy() as data:
        data['section'] = section

    result = db_manager.search_banner_id(section)
    new_caption = "Теперь давай выберем магазин:"
    await call.message.edit_media(types.InputMedia(media=result[0], caption=new_caption),
                                  reply_markup=get_store_kb(section))


async def enter_to_store(call: CallbackQuery):
    import main
    data = call.data.split("_")
    store = data[1]  # Получаем выбранный магазин
    results = db_manager.get_codes(store)
    result = db_manager.search_banner_id(store)
    await call.message.edit_media(types.InputMedia(media=result[0], caption="Вот что я нашёл для тебя:"))
    for elem in results:
        m_text = f"Промокод: <b>{elem[0]}</b>\n" \
                 f"<em>{elem[1]}</em>\n" \
                 f"Действителен до: <b>{elem[2]}</b>"
        await main.bot.send_message(call.message.chat.id, m_text, parse_mode="html", reply_markup=get_main_menu_kb())


async def back_to_main(call: CallbackQuery):
    new_caption = "Я постараюсь найти для тебя промокод, выбери раздел:"
    result = db_manager.search_banner_id("Default")
    await call.message.edit_media(types.InputMedia(media=result[0], caption=new_caption), reply_markup=get_section_kb())


def register_user_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(search_promo, text="Выбрать раздел")
    dp.register_message_handler(back_to_section, text="🔙 Выбрать магазин")
    dp.register_callback_query_handler(enter_to_section, lambda call: call.data.startswith("section_"))
    dp.register_callback_query_handler(enter_to_store, lambda call: call.data.startswith("store_"))
    dp.register_callback_query_handler(back_to_main, lambda call: call.data == "back_section")
