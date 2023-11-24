from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.utilities.data_base import DatabaseManager

# Создайте экземпляр класса DatabaseManager
db_manager = DatabaseManager()


def get_main_menu_kb() -> ReplyKeyboardMarkup:

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🔙 Выбрать магазин"))
    kb.add(KeyboardButton("Выбрать раздел"))

    return kb


# клавиатура разделов
def get_section_kb() -> InlineKeyboardMarkup:

    results = db_manager.get_section()
    list_of_section = sorted(list(set(results)))

    section_kb = InlineKeyboardMarkup(row_width=2)
    columns = 2
    rows = [list_of_section[i:i + columns] for i in range(0, len(list_of_section), columns)]
    for row in rows:
        row_buttons = [InlineKeyboardButton(text=elem, callback_data=f"section_{elem}") for elem in row]
        section_kb.add(*row_buttons)

    return section_kb


# клавиатура магазинов
def get_store_kb(section) -> InlineKeyboardMarkup:

    results = db_manager.get_store(section)
    list_of_store = sorted(list(set(results)))

    section_kb = InlineKeyboardMarkup(row_width=2)
    columns = 2
    rows = [list_of_store[i:i + columns] for i in range(0, len(list_of_store), columns)]
    for row in rows:
        row_buttons = [InlineKeyboardButton(text=elem, callback_data=f"store_{elem}") for elem in row]
        section_kb.add(*row_buttons)
    section_kb.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_section"))

    return section_kb
