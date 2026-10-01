class MinHeap:

    def __init__(self, key_func, id_func):
        self.heap = []
        self.key_func = key_func
        self.id_func = id_func

    def is_higher_priority(self, item1, item2):
        return self.key_func(item1) < self.key_func(item2)

    def insert(self, item):
        item_id = self.id_func(item)

        if item_id in self:
            raise ValueError(f"duplicate id pushed onto heap: {item_id!r}")

        self.heap.append(item)
        self._heapify_up(len(self.heap) - 1)

    def _heapify_up(self, index):
        while index > 0:
            parent = (index - 1) // 2

            if self.is_higher_priority(
                self.heap[index],
                self.heap[parent]
            ):
                self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
                index = parent
            else:
                break

    def extract_min(self):
        if len(self.heap) == 0:
            raise IndexError("pop from an empty heap")

        min_item = self.heap[0]
        last_item = self.heap.pop()

        if len(self.heap) > 0:
            self.heap[0] = last_item
            self._heapify_down(0)

        return min_item

    def remove_project(self, item_id):
        for i in range(len(self.heap)):

            if self.id_func(self.heap[i]) == item_id:
                removed_item = self.heap[i]
                last_item = self.heap.pop()

                if i < len(self.heap):
                    self.heap[i] = last_item

                    if i > 0:
                        parent = (i - 1) // 2

                        if self.is_higher_priority(
                            self.heap[i],
                            self.heap[parent]
                        ):
                            self._heapify_up(i)
                        else:
                            self._heapify_down(i)
                    else:
                        self._heapify_down(i)

                return removed_item

        return None

    def _heapify_down(self, index):
        size = len(self.heap)

        while True:
            left = 2 * index + 1
            right = 2 * index + 2
            smallest = index

            if left < size and self.is_higher_priority(
                self.heap[left],
                self.heap[smallest]
            ):
                smallest = left

            if right < size and self.is_higher_priority(
                self.heap[right],
                self.heap[smallest]
            ):
                smallest = right

            if smallest == index:
                break

            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            index = smallest

    def is_empty(self):
        return len(self.heap) == 0

    def size(self):
        return len(self.heap)

    def to_list(self):
        return list(self.heap)

    def display(self):
        if self.is_empty():
            print("Heap is empty.")
            return

        for item in self.heap:
            print(item)

    def __len__(self):
        return len(self.heap)

    def __contains__(self, item_id):
        for item in self.heap:
            if self.id_func(item) == item_id:
                return True
        return False

    # Website aliases. The logic still uses insert/extract_min/remove_project.
    def push(self, item):
        self.insert(item)

    def pop(self):
        return self.extract_min()

    def remove(self, item_id):
        result = self.remove_project(item_id)
        if result is None:
            raise KeyError(f"id not present in heap: {item_id!r}")
        return result

    @classmethod
    def build(cls, items, key_func, id_func):
        heap = cls(key_func, id_func)

        for item in items:
            heap.insert(item)

        return heap

