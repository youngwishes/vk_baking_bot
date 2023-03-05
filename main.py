import os
from keyboards import make_products_kb, make_categories_kb, make_main_menu_kb
from vk_bot.bot import VKBot
from vk_bot.types import User, Message
from states.states import CatalogState
import logging.config
from dict_config import dict_config
from vk_bot.db.conf import get_db_manager

logging.config.dictConfig(dict_config)


class MyBot(VKBot):
    logger = logging.getLogger('root')

    word_to_prev_state = "Назад 🛑"

    @staticmethod
    def unknown_command(message):
        bot.send_message(user_id=message.user_id, text="Неизвестная команда.")

    @staticmethod
    def main_menu(message: Message):
        user = User(user_id=message.user_id)
        bot.users_list.append(user)

        message_to_send = "Привет! Добро пожаловать в мою кондитерскую." \
                          " Выбери, что тебя интересует на клавиатуре."

        menu_kb = make_main_menu_kb()
        bot.send_message(user_id=message.user_id, text=message_to_send, keyboard=menu_kb.get_data(to_vk=True))


bot = MyBot(token=os.getenv("TOKEN"))


@bot.message_handler(commands=['Категории'], state=CatalogState(1))
def categories(message: Message):
    message_to_send = "Выбери категорию, которая тебе кажется наиболее вкусной =)"
    categories_keyboard = make_categories_kb()

    bot.send_message(
        user_id=message.user_id, text=message_to_send, keyboard=categories_keyboard.get_data(to_vk=True)
    )


@bot.message_handler(state=CatalogState(2), need_to_miss_if_back=True)
def categories_and_products(message: Message):
    products_kb = make_products_kb(message)

    bot.send_message(user_id=message.user_id, text="Вот, что у меня есть!'", keyboard=products_kb.get_data(to_vk=True))


@bot.message_handler(state=CatalogState(3))
def check_product(message):
    product = db_manager.get_product(message.text)
    if not product:
        bot.send_message(user_id=message.user_id, text="Не нашел выпечку :(")
    else:
        with open(product.image, 'rb') as img:
            bot.send_message(user_id=message.user_id, text=f'{product.name}\n{product.description}', photo=img)


if __name__ == '__main__':
    db_manager = get_db_manager()
    bot.longpolling()
