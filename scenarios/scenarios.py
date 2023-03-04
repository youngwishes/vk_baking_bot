from vk_bot.mixins import SingleToneMixin


class Scenario(SingleToneMixin):
    def __init__(self):
        self.tail = None
        self.head = None

    def append(self, node):
        if not self.tail and not self.head:
            self.head = node
            self.tail = node
        else:
            if self.tail is not self.head:
                prev_tail = self.tail
                prev_tail.next = node
                self.tail = node
                self.tail.prev = prev_tail
            else:
                self.tail = node
                self.head.next = self.tail
                self.tail.prev = self.head

    def __str__(self):
        str_data = f"{self.__class__.__name__}["
        if self.head:
            str_data += f'{self.head} -> '
            node = self.head
            while node.next:
                str_data += f'{node.next} -> '
                node = node.next

        str_data += 'None]'

        return str_data

    def __len__(self):
        count = 1
        node = self.head
        while node.next:
            count += 1
            node = node.next

        return count

    def __getitem__(self, item):
        count = 0
        node = self.head
        while node.next or count == item:
            if count == item:
                return node

            node = node.next
            count += 1

        raise IndexError


class CatalogScenario(Scenario):
    pass
