"""Hand-implemented singly linked list.

Used for the damaged-items log: an append-only, traverse-in-order record
of damage reports. Complexity (n = number of nodes):
    append()   O(1)  - a tail pointer is kept, so no traversal is needed
    traverse() O(n)  - must visit every node once
    __len__()  O(1)  - maintained as a running counter
"""

from typing import Generic, Iterator, TypeVar

T = TypeVar("T")


class _Node(Generic[T]):
    __slots__ = ("value", "next")

    def __init__(self, value: T):
        self.value = value
        self.next: "_Node[T] | None" = None


class SinglyLinkedList(Generic[T]):
    def __init__(self):
        self._head: _Node[T] | None = None
        self._tail: _Node[T] | None = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._head is None

    def append(self, value: T) -> None:
        node = _Node(value)
        if self._tail is None:
            self._head = self._tail = node
        else:
            self._tail.next = node
            self._tail = node
        self._size += 1

    def traverse(self) -> Iterator[T]:
        node = self._head
        while node is not None:
            yield node.value
            node = node.next

    def __iter__(self) -> Iterator[T]:
        return self.traverse()

    def to_list(self) -> list[T]:
        return list(self.traverse())
