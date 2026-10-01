class HashNode:

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None


class HashTable:

    def __init__(self, size=101):
        self.size = size
        self.table = [None] * size
        self.count = 0

    def _hash(self, key):
        total = 0

        for char in str(key):
            total += ord(char)

        return total % self.size

    def insert(self, key, value):
        index = self._hash(key)
        current = self.table[index]

        while current is not None:
            if current.key == key:
                current.value = value
                return
            current = current.next

        new_node = HashNode(key, value)

        if self.table[index] is None:
            self.table[index] = new_node
        else:
            new_node.next = self.table[index]
            self.table[index] = new_node

        self.count += 1

    def search(self, key, default=None):
        index = self._hash(key)
        current = self.table[index]

        while current is not None:
            if current.key == key:
                return current.value
            current = current.next

        return default

    def delete(self, key):
        index = self._hash(key)
        current = self.table[index]
        previous = None

        while current is not None:
            if current.key == key:
                if previous is None:
                    self.table[index] = current.next
                else:
                    previous.next = current.next

                self.count -= 1
                return current.value

            previous = current
            current = current.next

        return None

    def keys(self):
        for bucket in self.table:
            current = bucket

            while current is not None:
                yield current.key
                current = current.next

    def values(self):
        for bucket in self.table:
            current = bucket

            while current is not None:
                yield current.value
                current = current.next

    def items(self):
        for bucket in self.table:
            current = bucket

            while current is not None:
                yield current.key, current.value
                current = current.next

    def is_empty(self):
        return self.count == 0

    def __len__(self):
        return self.count

    def __contains__(self, key):
        index = self._hash(key)
        current = self.table[index]

        while current is not None:
            if current.key == key:
                return True
            current = current.next

        return False

    # Website aliases. The underlying operations are William-style
    # insert/search/delete with separate chaining through node.next.
    def put(self, key, value):
        self.insert(key, value)

    def get(self, key, default=None):
        return self.search(key, default)

