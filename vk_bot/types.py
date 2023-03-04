class Message:
    def __init__(self, data):
        self.user_id = data['updates'][0]['object']['message']['from_id']
        self.random_id = data['updates'][0]['object']['message']['id']
        self.text = data['updates'][0]['object']['message']['text']


class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.state = None


class UsersList:
    users_list = []

    def append(self, new_user):
        for user in self.users_list:
            if user.user_id == new_user.user_id:
                user.state = None
                return
        self.users_list.append(new_user)

    def get_user_by_id(self, user_id):
        for user in self.users_list:
            if user.user_id == user_id:
                return user
