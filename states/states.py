from typing import Callable
from scenarios.scenarios import CatalogScenario


class State:
    """
    Это состояние, которое используется в сценариях. Каждое состояние знает,
    какое состояние будет следующим и какое было предыдущим.

    :scenario: - Сценарий, в котором используется это состояние.
    :self.value: - Сюда попадает функция, которая соответствует текущему состоянию.
    :self.need_to_miss_if_back: - Нужно ли пропускать это состояние, при возвращении на предыдущее состояние
    :self.prev: - Ссылка на предыдущее состояние
    :self.next: - Ссылка на следующее состояние
    """
    scenario = None

    def __init__(self, value):
        self.value = value
        self.need_to_miss_if_back = None
        self.prev = None
        self.next = None

    def __str__(self):
        if isinstance(self.value, Callable):
            return f'{self.value.__name__}'
        return f'{self.value}'

    def add_to_scenario(self):
        self.scenario.append(self)


class CatalogState(State):
    scenario = CatalogScenario()
