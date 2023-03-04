from typing import Callable
from scenarios.scenarios import CatalogScenario


class State:
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


class CatalogState(State):
    scenario = CatalogScenario()

    def add_to_scenario(self):
        self.scenario.append(self)
