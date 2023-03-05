from unittest import TestCase
from scenarios.scenarios import Scenario
from states.states import State


class TestScenario(TestCase):
    def setUp(self) -> None:
        self.scenario = Scenario()
        for i in range(100):
            self.scenario.append(State(i))

    def test_scenario_list_indexes(self):
        for index, node in enumerate(self.scenario):
            self.assertEqual(self.scenario[index], node)

    def test_tail_is_last_elem(self):
        self.assertEqual(self.scenario.tail, self.scenario[len(self.scenario) - 1])

    def test_head_is_first_elem(self):
        self.assertEqual(self.scenario.head, self.scenario[0])

    def test_scenario_states_next_values(self):
        for index, node in enumerate(self.scenario):
            if index < len(self.scenario) - 1:
                self.assertEqual(node.next, self.scenario[index + 1])
            else:
                self.assertEqual(node.next, None)

    def test_scenario_states_prev_values(self):
        for index, node in enumerate(self.scenario):
            if node.prev:
                if index < len(self.scenario):
                    self.assertEqual(node.prev, self.scenario[index - 1])

    def test_from_tail_to_head(self):
        tail = self.scenario.tail

        while tail.prev:
            tail = tail.prev

        self.assertEqual(tail, self.scenario.head)

    def test_from_head_to_tail(self):
        head = self.scenario.head

        while head.next:
            head = head.next

        self.assertEqual(head, self.scenario.tail)

    def test_from_head_to_tail_to_head(self):
        head = self.scenario.head

        while head.next:
            head = head.next

        while head.prev:
            head = head.prev

        self.assertEqual(head, self.scenario.head)

    def test_from_tail_to_head_to_tail(self):
        tail = self.scenario.tail

        while tail.prev:
            tail = tail.prev

        while tail.next:
            tail = tail.next

        self.assertEqual(tail, self.scenario.tail)
