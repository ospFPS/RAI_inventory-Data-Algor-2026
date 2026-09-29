"""Hand-implemented binary min-heap with an id -> index position map.

Complexity (n = number of items currently in the heap):
    peek()          O(1)        - root of the array is always the minimum
    push()           O(log n)    - append + sift-up along one root path
    pop()            O(log n)    - swap root/last, remove, sift-down
    remove(id)       O(log n)    - position map gives O(1) lookup of the
                                    item's index, then one sift-up/sift-down
    build(items)     O(n)        - bottom-up heapify (not n log n): the
                                    classic amortized analysis sums
                                    sift-down cost over all subtree heights,
                                    which telescopes to O(n), not O(n log n)

The position map (id -> index) is what makes remove()/update() O(log n)
instead of O(n). Without it, deleting an arbitrary project's request from
the queue (e.g. a project that got returned early) would require an O(n)
linear scan to find it first.
"""

from typing import Callable, Generic, Hashable, Iterable, TypeVar

T = TypeVar("T")
K = TypeVar("K")


class HeapItem(Generic[T]):
    """Not required by callers directly; MinHeap wraps/unwraps payloads."""

    __slots__ = ("key", "id", "payload")

    def __init__(self, key: K, id_: Hashable, payload: T):
        self.key = key
        self.id = id_
        self.payload = payload


class MinHeap(Generic[T]):
    """Array-backed binary min-heap keyed by ``key_func(item)``.

    ``id_func(item)`` must return a hashable, unique id for each item so
    that :meth:`remove` and :meth:`update_key` can locate it in O(log n)
    via the internal position map, instead of scanning the array.
    """

    def __init__(self, key_func: Callable[[T], K], id_func: Callable[[T], Hashable]):
        self._key_func = key_func
        self._id_func = id_func
        self._items: list[HeapItem[T]] = []
        self._pos: dict[Hashable, int] = {}  # id -> index in self._items

    def __len__(self) -> int:
        return len(self._items)

    def is_empty(self) -> bool:
        return not self._items

    def __contains__(self, id_: Hashable) -> bool:
        return id_ in self._pos

    @classmethod
    def build(
        cls,
        items: Iterable[T],
        key_func: Callable[[T], K],
        id_func: Callable[[T], Hashable],
    ) -> "MinHeap[T]":
        """Heapify an existing collection in O(n) (bottom-up sift-down)."""
        heap = cls(key_func, id_func)
        heap._items = [HeapItem(key_func(x), id_func(x), x) for x in items]
        heap._pos = {node.id: i for i, node in enumerate(heap._items)}
        n = len(heap._items)
        for i in range(n // 2 - 1, -1, -1):
            heap._sift_down(i)
        return heap

    def to_list(self) -> list[T]:
        """Non-destructive O(n) snapshot of payloads in internal array
        order (heap-ordered, but *not* fully sorted). Callers that need
        a fully priority-ordered listing for display should sort this
        with algo.merge_sort rather than relying on array order."""
        return [node.payload for node in self._items]

    def peek(self) -> T:
        if not self._items:
            raise IndexError("peek from an empty heap")
        return self._items[0].payload

    def push(self, item: T) -> None:
        id_ = self._id_func(item)
        if id_ in self._pos:
            raise ValueError(f"duplicate id pushed onto heap: {id_!r}")
        node = HeapItem(self._key_func(item), id_, item)
        self._items.append(node)
        i = len(self._items) - 1
        self._pos[id_] = i
        self._sift_up(i)

    def pop(self) -> T:
        """Extract and return the minimum item."""
        if not self._items:
            raise IndexError("pop from an empty heap")
        return self._remove_at(0)

    def remove(self, id_: Hashable) -> T:
        """Remove and return the item with the given id, wherever it sits."""
        if id_ not in self._pos:
            raise KeyError(f"id not present in heap: {id_!r}")
        return self._remove_at(self._pos[id_])

    def update_key(self, id_: Hashable, item: T) -> None:
        """Re-key an existing item (e.g. payload changed) and re-heapify it."""
        if id_ not in self._pos:
            raise KeyError(f"id not present in heap: {id_!r}")
        i = self._pos[id_]
        node = self._items[i]
        node.payload = item
        node.key = self._key_func(item)
        # The new key could be smaller or larger than before, so it may
        # need to move in either direction.
        self._sift_up(i)
        self._sift_down(self._pos[id_])

    # -- internal helpers ------------------------------------------------

    def _remove_at(self, i: int) -> T:
        last = len(self._items) - 1
        self._swap(i, last)
        node = self._items.pop()
        del self._pos[node.id]
        if i <= last - 1:
            # The element swapped into position i could belong either
            # above or below where it landed.
            self._sift_down(i)
            self._sift_up(i)
        return node.payload

    def _swap(self, i: int, j: int) -> None:
        self._items[i], self._items[j] = self._items[j], self._items[i]
        self._pos[self._items[i].id] = i
        self._pos[self._items[j].id] = j

    def _sift_up(self, i: int) -> None:
        while i > 0:
            parent = (i - 1) // 2
            if self._items[i].key < self._items[parent].key:
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i: int) -> None:
        n = len(self._items)
        while True:
            left, right = 2 * i + 1, 2 * i + 2
            smallest = i
            if left < n and self._items[left].key < self._items[smallest].key:
                smallest = left
            if right < n and self._items[right].key < self._items[smallest].key:
                smallest = right
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest
