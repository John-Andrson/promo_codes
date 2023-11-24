import os
import time
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot.client.handlers.user_handlers import register_user_handlers
from bot.admin.handlers.admin_handlers import register_admin_handlers
from bot.admin.handlers.adding import register_adding_handlers
from bot.admin.handlers.edit import register_edit_handlers
from bot.admin.handlers.banners import register_banners_handlers


# конфигурация
storage = MemoryStorage()
load_dotenv('.env')
token = os.getenv("TOKEN_API")
bot = Bot(token)
dp = Dispatcher(bot, storage=storage)


# регистрация хэндлеров
def register_handler() -> None:
    register_user_handlers(dp)
    register_admin_handlers(dp)
    register_adding_handlers(dp)
    register_edit_handlers(dp)
    register_banners_handlers(dp)


# вызов хэндлеров
register_handler()


# чистка спама
@dp.message_handler()
async def chat_cleaning(msg: types.Message):
    time.sleep(2)
    await msg.delete()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
