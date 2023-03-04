import os
from keyboards import VKeyboard, Button
from vk_bot.bot import VKBot
from vk_bot.types import User, Message
from states.states import CatalogState
import logging.config
from dict_config import dict_config
from vk_bot.db.conf import get_db_manager


class MyBot(VKBot):
    logger = logging.getLogger('root')
    logging.config.dictConfig(dict_config)
    word_to_prev_state = "Назад 🛑"

    @staticmethod
    def unknown_command_handler(message):
        bot.send_message(user_id=message.user_id, text="Неизвестная команда.")


bot = MyBot(token=os.getenv("TOKEN"))


@bot.message_handler()
def unknown_command_handler(message: Message):
    bot.send_message(user_id=message.user_id, text="Неизвестная команда.")


@bot.message_handler(commands=['Начать'], is_menu=True)
def welcome(message: Message):
    user = User(user_id=message.user_id)
    bot.users_list.append(user)

    message_to_send = "Привет! Добро пожаловать в мою кондитерскую." \
                      " Выбери, что тебя интересует на клавиатуре."

    menu_kb = make_main_menu_kb()
    bot.send_message(user_id=message.user_id, text=message_to_send, keyboard=menu_kb.get_data(to_vk=True))


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
    bot.send_message(user_id=message.user_id, text='Вот, что у меня есть!', keyboard=products_kb.get_data(to_vk=True))


@bot.message_handler(state=CatalogState(3))
def check_product(message):
    product = db_manager.get_product(message.text)

    with open(product.image, 'rb') as img:
        bot.send_message(user_id=message.user_id, text=f'{product.name}\n{product.description}', photo=img)


def make_main_menu_kb():
    menu_kb = VKeyboard('menu.json', one_time=False)
    b1 = Button(label='Категории')

    menu_kb.add_button(b1)

    return menu_kb


def make_categories_kb():
    categories_keyboard = VKeyboard('categories.json', one_time=False)
    for cat in db_manager.get_categories():
        categories_keyboard.add_button(Button(label=cat.name, color="primary"))


    return categories_keyboard


def make_products_kb(message):
    products_keyboard = VKeyboard('products.json', one_time=False)
    for product in db_manager.get_products(message.text):
        products_keyboard.add_button(Button(label=product.name))

    return products_keyboard


if __name__ == '__main__':
    db_manager = get_db_manager()
    bot.longpolling()
