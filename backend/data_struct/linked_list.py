class DamageNode:

    def __init__(self, value):
        self.value = value
        self.next = None


class SinglyLinkedList:

    def __init__(self):
        self.head = None
        self.tail = None
        self.count = 0

    def append(self, value):
        new_node = DamageNode(value)

        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

        self.count += 1

    def traverse(self):
        current = self.head

        while current is not None:
            yield current.value
            current = current.next

    def is_empty(self):
        return self.head is None

    def to_list(self):
        return list(self.traverse())

    def __len__(self):
        return self.count

    def __iter__(self):
        return self.traverse()

