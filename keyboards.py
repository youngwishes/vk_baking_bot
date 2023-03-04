import json
import os


class Button:
    def __init__(self, label, button_type="text", color="secondary"):
        self.label = label
        self.button_type = button_type
        self.color = color
        self.count = 0

    def as_json(self):
        return {
            "action": {
                "type": self.button_type,
                "label": self.label
            },
            "color": self.color
        }

    def __str__(self):
        return f'Button(label={self.label}, type={self.button_type}, color={self.color})'


class VKeyboard:
    def __init__(self, path, one_time=False):
        self.one_time = one_time
        self.path = path
        self.count = -1

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, filename):
        if not filename.endswith('json'):
            raise ValueError("Формат файла клавиатуры должен быть json.")

        if 'keyboards_json' not in os.listdir():
            os.makedirs('keyboards_json')

        self._path = os.path.join('keyboards_json', filename)

        with open(self._path, 'w', encoding='utf-8') as f:
            data = {
                "one_time": self.one_time,
                "buttons": []
            }

            json.dump(data, f, indent=4)

    def set_data(self, json_data):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4)

    def add_button(self, button):
        print(button)
        json_data = self.get_data(to_vk=False)
        if self.count == -1:
            json_data['buttons'].append([button.as_json()])
            self.count += 1
            self.set_data(json_data)
        else:
            json_data['buttons'][-1].append(button.as_json())
            self.set_data(json_data)
            self.count = -1

    def add_row(self, *args):
        buttons_list = []

        for button in args:
            buttons_list.append({
                "action": {
                    "type": button.button_type,
                    "label": button.label
                },
                "color": button.color
            })

        json_data = self.get_data(to_vk=False)

        json_data['buttons'].append(buttons_list)

        self.set_data(json_data)

    def get_data(self, to_vk=False):
        if to_vk:
            self.add_row(Button(label="Меню 🔍", color="positive"), Button(label="Назад 🛑", color="negative"))

        with open(self.path, 'r', encoding='utf-8') as f:
            return f.read() if to_vk else json.loads(f.read())
