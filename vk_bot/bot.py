import requests
from random import randint
import threading
from .types import Message, UsersList


class VKBot:
    """
    __longpoll_url: (Документация) https://dev.vk.com/method/groups.getLongPollServer
    __send_message_url: (Документация) https://dev.vk.com/method/messages.send
    __photo_server_url: (Документация) https://dev.vk.com/method/photos.getMessagesUploadServer
    __save_photo_url: (Документация) https://dev.vk.com/method/photos.saveMessagesPhoto
    __version: Версия API
    __group_id: ID группы в VK
    logger: Логгер
    users_list: Список пользователей, которые пользуются ботом
    word_to_prev_state: Ключевое слово, чтобы вернуться на предыдущее состояние в машине состояний
    """

    __longpoll_url = 'https://api.vk.com/method/groups.getLongPollServer'
    __send_message_url = 'https://api.vk.com/method/messages.send'
    __photo_server_url = "https://api.vk.com/method/photos.getMessagesUploadServer"
    __save_photo_url = "https://api.vk.com/method/photos.saveMessagesPhoto"

    __version = '5.131'
    __group_id = '218434110'
    logger = None
    users_list = UsersList()
    word_to_prev_state = "Назад 🛑"

    def __init__(self, token):
        """

        :param token: Токен бота
        :var self._data: key, server, ts в виде словаря
        :var self.message_handlers: Список с обработчиками сообщений (функции под декоратором message_handler).
        """
        self.__token = token
        self._data = self.get_longpoll_data()

        self.message_handlers = []

        for key, value in self._data.items():
            setattr(self, key, value)

        self.logger.info("VK Bot was successfully initialized 🤖.")

    def get_longpoll_url_params(self):
        return {
            'access_token': self.__token,
            'v': self.__version,
            'group_id': self.__group_id,
        }

    def get_longpoll_data(self):
        response = requests.get(self.__longpoll_url, params=self.get_longpoll_url_params())

        if response.status_code == 200:
            return response.json()['response']

    def _get_longpoll_check_params(self):
        params = {
            key: f'{getattr(self, key)}' for key in self._data
        }
        params['wait'] = 15
        params['act'] = 'a_check'

        return params

    def _get_photo_server(self):
        """
        Функция делающая запрос на "https://api.vk.com/method/photos.getMessagesUploadServer"

        :return: url, куда грузить фотки
        """
        response = requests.get(self.__photo_server_url, params={'access_token': self.__token, 'v': self.__version})
        upload_url = response.json()['response']['upload_url']
        return upload_url

    def _save_photo(self, hash, server, photo):
        """
        Параметры, которые возвращаются после запроса на URL,
        который возвращает функция _get_photo_server

        """
        params = {
            'access_token': self.__token,
            'v': self.__version,
            'hash': hash,
            'server': server,
            'photo': photo
        }

        response = requests.post(self.__save_photo_url, data=params)

        owner_id = response.json()['response'][0]['owner_id']
        id_ = response.json()['response'][0]['id']

        return f'photo{owner_id}_{id_}'

    def get_photo(self, photo):
        """
        :param photo: Фотография которую нужно отправить пользователю
        """
        upload_url = self._get_photo_server()
        response = requests.post(upload_url, files={'photo': photo})

        return self._save_photo(**response.json())

    def send_message(self, user_id, text, keyboard=None, photo=None):
        """
        :param user_id: Кому отправляем
        :param text: Что отправляем
        :param keyboard: Есть ли клавиатура
        :param photo: Есть ли фотка
        """
        if photo:
            photo = self.get_photo(photo)

        params = {
            'user_id': user_id,
            'random_id': randint(-(10 ** 7), 10 ** 7),
            'message': text,
            'access_token': self.__token,
            'v': self.__version,
            'keyboard': keyboard,
            'attachment': photo
        }

        self.logger.debug(f"🤖 will send the message with params:\n{params}")
        requests.post(self.__send_message_url, data=params)
        self.logger.info(f"🤖 has sent the message: '{text}'")

    def longpolling(self):
        """
        Реализация длинных запросов
        :return:
        """
        params = self._get_longpoll_check_params()
        server = params['server']
        self.logger.debug(f"🤖 will send the request to the server: {server}\nparams: {params}")

        with requests.Session() as session:
            while True:
                self.logger.info(f"🤖 has sent a long request and waiting for the event...")
                response = session.get(server, params=params)
                params['ts'] = self.get_longpoll_data()['ts']

                if response.json().get('updates'):
                    self.logger.debug(f"🤖 just got a new updates.")
                    data = response.json()
                    event_type = data.get('updates')[0].get('type')
                    if event_type == "message_new":
                        self.logger.info(f"🤖 just got a message. He is thinking what he need answer...")
                        threading.Thread(target=self._handle, args=(Message(data),)).start()

    @staticmethod
    def _build_handler_dict(handler, **kwargs):
        """
        :param handler: Функция-обработчик сообщений (под декоратором message_handler)
        :param kwargs: Параметры декоратора
        :return:
        """
        handler_dict = {
            key: kwargs[key] for key in kwargs
        }
        handler_dict['function'] = handler

        return handler_dict

    def message_handler(self, commands=None, state=None, need_to_miss_if_back=None):
        """
        :param commands: Команды, на которые реагирует функция
        :param state: Состояние, которая описывает данная функция
        :param need_to_miss_if_back: Нужно ли пропускать это состояние, если пользователь нажимает "Назад"
        :return:
        """

        def wrapper(handler):
            """
            Построение сценариев, создание хендлеров, добавление хендлеров в список
            :param handler:
            :return:
            """

            if state:
                state.value = handler
                state.need_to_miss_if_back = need_to_miss_if_back
                state.add_to_scenario()

                self.logger.info(f"Scenario was successfully updated: {state.scenario}")

            handler_dict = self._build_handler_dict(
                state or handler, commands=commands if commands else [], state=state
            )

            self.message_handlers.append(handler_dict)
            return handler

        return wrapper

    def _handle(self, message):
        """
        Здесь происходит вся логика работы состояний, эта функция отвечает за то, какой сработает message_handler.
        :param message: Сообщение пользователя
        :return:
        """
        user = self.users_list.get_user_by_id(message.user_id)

        if not user or message.text == "Меню 🔍":
            return self.main_menu(message)

        self.logger.info(f"User has {user.state} state.")

        if message.text == self.word_to_prev_state:
            return self.get_previous_state(user, message)

        if not user.state:
            is_specified = self.set_user_state(user, message)
            if not is_specified:
                return self.unknown_command(message)
            return user.state.value(message)

        if user.state.next:
            user.state = user.state.next
            return user.state.value(message)

        return user.state.value(message)

    def set_user_state(self, user, message):
        """
        Установка состояния пользователя
        :param user: Пользователь
        :param message: Сообщение
        :return:
        """
        for handler in self.message_handlers:
            if message.text in handler['commands']:
                state = handler['state']

                if state == state.scenario[0]:
                    user.state = handler['state']
                    return True

    def get_previous_state(self, user, message):
        """
        Работа с командой "Назад 🛑". Проверка предыдущего состояния.
        :param user: Пользователь
        :param message: Сообщение
        :return: State.value
        """
        if user.state:
            if user.state.prev:
                user.state = user.state.prev
                while user.state.need_to_miss_if_back:
                    user.state = user.state.prev
                return user.state.value(message)
            else:
                return self.main_menu(message)

    @staticmethod
    def unknown_command(message):
        """
        Функция срабатывает, когда у пользователя нет состояния и он вводит незнакомую боту команду.
        Необходимо переопределить в наследнике
        :param message: Сообщение
        :return:
        """
        pass

    @staticmethod
    def main_menu(message):
        """
        Функция срабатывает, когда пользователь вводит "Меню 🔍" ИЛИ он еще не добавлен в список пользователей.
        Необходимо переопределить в наследнике
        :param message: Сообщение
        :return:
        """
        pass
