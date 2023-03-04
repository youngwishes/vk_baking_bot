import requests
from random import randint
import threading
from .types import Message, UsersList


class VKBot:
    __longpoll_url = 'https://api.vk.com/method/groups.getLongPollServer'
    __send_message_url = 'https://api.vk.com/method/messages.send'
    __photo_server_url = "https://api.vk.com/method/photos.getMessagesUploadServer"
    __save_photo_url = "https://api.vk.com/method/photos.saveMessagesPhoto"

    __version = '5.131'
    __group_id = '218434110'
    logger = None
    users_list = UsersList()
    wort_to_prev_state = "Назад 🛑"

    def __init__(self, token):
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

    @staticmethod
    def _build_handler_dict(handler, **kwargs):
        return {
            'function': handler,
            'commands': kwargs['commands'] if kwargs['commands'] else [],
            'state': kwargs['state'],
            'is_menu': kwargs['is_menu'],
        }

    def _get_photo_server(self):
        response = requests.get(self.__photo_server_url, params={'access_token': self.__token, 'v': self.__version})
        upload_url = response.json()['response']['upload_url']
        return upload_url

    def _save_photo(self, hash, server, photo):
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
        upload_url = self._get_photo_server()
        response = requests.post(upload_url, files={'photo': photo})

        return self._save_photo(**response.json())

    def send_message(self, user_id, text, keyboard=None, photo=None):

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

    def message_handler(self, commands=None, is_menu=None, state=None, need_to_miss_if_back=None):
        def wrapper(handler):
            if state:
                state.value = handler
                state.need_to_miss_if_back = need_to_miss_if_back
                state.add_to_scenario()

                self.logger.info(f"Scenario was successfully updated: {state.scenario}")

            handler_dict = self._build_handler_dict(
                state or handler, commands=commands,
                state=state, is_menu=is_menu
            )

            self.message_handlers.append(handler_dict)
            return handler

        return wrapper

    def set_user_state(self, user, message):
        for handler in self.message_handlers:
            if message.text in handler['commands']:
                state = handler['state']

                if state == state.scenario[0]:
                    user.state = handler['state']
                    return True

        return self.unknown_command(message)

    def _handle(self, message):
        user = self.users_list.get_user_by_id(message.user_id)

        if not user or message.text == "Меню 🔍":
            main_menu = list(filter(lambda handler: handler['is_menu'], self.message_handlers))[0]
            return main_menu['function'](message)

        self.logger.info(f"User has {user.state} state.")

        if message.text == self.wort_to_prev_state:
            return self.get_previous_state(user, message)

        if not user.state:
            is_specified = self.set_user_state(user, message)
            if not is_specified:
                return False
            return user.state.value(message)

        if user.state.next:
            user.state = user.state.next
            return user.state.value(message)

        return user.state.value(message)

    def get_previous_state(self, user, message):
        if user.state:
            if user.state.prev:
                user.state = user.state.prev
                while user.state.need_to_miss_if_back:
                    user.state = user.state.prev

                return user.state.value(message)
            else:
                main_menu = list(filter(lambda handler: handler['is_menu'], self.message_handlers))[0]
                return main_menu['function'](message)

    def unknown_command(self, message):
        pass
