from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.utilities.data_base import DatabaseManager

# Создайте экземпляр класса DatabaseManager
db_manager = DatabaseManager()


# выбор категории баннеров
def get_menu_banners_kb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=3)
    b0 = InlineKeyboardButton(text="для разделов", callback_data="for_section")
    b1 = InlineKeyboardButton(text="для магазинов", callback_data="for_store")
    b2 = InlineKeyboardButton(text="баннер по умолчанию", callback_data="default")
    b6 = InlineKeyboardButton(text="Назад", callback_data="back_in_main")
    ikb.add(b0, b1).add(b2).add(b6)
    return ikb


# меню управления баннерами
def get_banners_control_kb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=3)
    b1 = InlineKeyboardButton(text="Изменить", callback_data="banners_edit")
    b2 = InlineKeyboardButton(text="Удалить", callback_data="banners_delete")
    b6 = InlineKeyboardButton(text="Назад", callback_data="back_in_menu_banners")
    ikb.add(b1, b2).add(b6)
    return ikb


# клавиатура разделов
def get_section_kb() -> InlineKeyboardMarkup:

    results = db_manager.get_section()
    list_of_section = sorted(list(set(results)))

    section_kb = InlineKeyboardMarkup(row_width=2)
    b6 = InlineKeyboardButton(text="Назад", callback_data="back_in_menu_banners")
    columns = 2
    rows = [list_of_section[i:i + columns] for i in range(0, len(list_of_section), columns)]
    for row in rows:
        row_buttons = [InlineKeyboardButton(text=elem, callback_data=f"chbanner_{elem}") for elem in row]
        section_kb.add(*row_buttons)
    section_kb.add(b6)

    return section_kb


# клавиатура магазинов
def get_store_kb() -> InlineKeyboardMarkup:

    results = db_manager.get_all_stores()
    list_of_section = sorted(list(set(results)))

    store_kb = InlineKeyboardMarkup(row_width=2)
    b6 = InlineKeyboardButton(text="Назад", callback_data="back_in_menu_banners")
    columns = 2
    rows = [list_of_section[i:i + columns] for i in range(0, len(list_of_section), columns)]
    for row in rows:
        row_buttons = [InlineKeyboardButton(text=elem, callback_data=f"chbanner_{elem}") for elem in row]
        store_kb.add(*row_buttons)
    store_kb.add(b6)

    return store_kb
