from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.utilities.data_base import DatabaseManager

# Создайте экземпляр класса DatabaseManager
db_manager = DatabaseManager()


# меню админа
def get_menu_admin_kb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=3)
    b0 = InlineKeyboardButton(text="Баннеры", callback_data="banners")
    b1 = InlineKeyboardButton(text="Добавить", callback_data="adding")
    b3 = InlineKeyboardButton(text="Редактировать", callback_data="edit")
    b4 = InlineKeyboardButton(text="Рассылка", callback_data="sending")
    b5 = InlineKeyboardButton(text="Выгрузка", callback_data="download")
    b6 = InlineKeyboardButton(text="Закрыть", callback_data="close")
    ikb.add(b0, b1, b3).add(b4, b5).add(b6)
    return ikb


# меню рассылки
def get_all_users_kb() -> ReplyKeyboardMarkup:

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Отправить всем"))
    kb.add(KeyboardButton("🔙 Вернуться в меню администратора"))

    return kb


# старт рассылки
def get_start_sending_kb() -> ReplyKeyboardMarkup:

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Начать рассылку"))
    kb.add(KeyboardButton("🔙 Вернуться в меню администратора"))

    return kb


# отмена рассылки
def get_cancel_sending_kb() -> ReplyKeyboardMarkup:

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🔙 Вернуться в меню администратора"))

    return kb


# выход в меню пользователя
def get_user_menu_kb() -> ReplyKeyboardMarkup:

    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Выбрать раздел"))

    return kb


# клавиатура шаблонов разделов
def get_section_kb() -> ReplyKeyboardMarkup:

    results = db_manager.get_section()
    list_of_section = sorted(list(set(results)))

    buttons = [KeyboardButton(text=section) for section in list_of_section]
    button = KeyboardButton(text="Отмена")
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(*buttons).add(button)
    return keyboard


# клавиатура шаблонов магазинов
def get_store_kb(section) -> ReplyKeyboardMarkup:

    results = db_manager.get_store(section)
    list_of_section = sorted(list(set(results)))

    buttons = [KeyboardButton(text=section) for section in list_of_section]
    button = KeyboardButton(text="Отмена")
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(*buttons).add(button)
    return keyboard


# клавиатура отмены
def get_cancel_kb() -> ReplyKeyboardMarkup:

    button = KeyboardButton(text="Отмена")
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(button)
    return keyboard


# клавиатура выбора даты
def get_date_kb() -> ReplyKeyboardMarkup:
    button1 = KeyboardButton(text="Не указывать дату")
    button2 = KeyboardButton(text="Отмена")
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(button1, button2)
    return keyboard


# клавиатура для перехода в меню админа или пользователя
def get_in_menu_kb() -> ReplyKeyboardMarkup:
    button1 = KeyboardButton(text="Вернуться в меню пользователя")
    button2 = KeyboardButton(text="Вернуться в меню администратора")
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(button1).add(button2)
    return keyboard


# редактировать/удалить
def get_edit_delete_kb(p_id) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=3)
    b1 = InlineKeyboardButton(text="Удалить", callback_data=f"delete_{p_id}")
    b3 = InlineKeyboardButton(text="Изменить", callback_data=f"change_{p_id}")
    b6 = InlineKeyboardButton(text="Закрыть", callback_data="close_record")
    ikb.add(b1, b3).add(b6)
    return ikb


# редактирование
def get_edit_record_kb() -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=3)
    b1 = InlineKeyboardButton(text="Раздел", callback_data="edit_section")
    b2 = InlineKeyboardButton(text="Магазин", callback_data="edit_store")
    b3 = InlineKeyboardButton(text="Промо-код", callback_data="edit_code")
    b4 = InlineKeyboardButton(text="Описание", callback_data="edit_description")
    b5 = InlineKeyboardButton(text="Дату", callback_data="edit_date")
    b6 = InlineKeyboardButton(text="Статус", callback_data="edit_status")
    b7 = InlineKeyboardButton(text="Отмена", callback_data="cancel_edit_rec")
    ikb.add(b1, b2, b3, b4, b5, b6, b7)
    return ikb
