"""Hand-implemented hash table with separate chaining.

Hash function: FNV-1a (a standard, cheap, well-distributed string hash),
applied to ``repr(key)`` so any hashable-by-repr key (str, tuple of
str/int, ...) works without relying on Python's built-in ``hash()``.

    h = 2166136261                      (FNV offset basis, 32-bit)
    for each byte b in repr(key):
        h = (h XOR b) * 16777619 mod 2**32   (FNV prime)
    index = h mod capacity

Load factor and resizing: load_factor = len / capacity. Every put() that
would push load_factor above ``MAX_LOAD_FACTOR`` (0.75) doubles capacity
and rehashes all entries into new buckets first. This keeps the expected
chain length, and therefore expected get/put/delete cost, at O(1);
resize itself is O(n) but amortizes to O(1) per put over a sequence of
insertions (the usual doubling-array argument).

Worst case for any single operation is O(m) (m = number of entries),
which only happens if every key collides into the same bucket -- e.g. an
adversarial or degenerate hash function. FNV-1a over distinct project
IDs / (type, item_name) pairs does not do that in practice, but it is
still a hash table's documented worst case.
"""

from typing import Generic, Hashable, Iterator, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")

_FNV_OFFSET_BASIS = 2166136261
_FNV_PRIME = 16777619
_MASK_32 = 0xFFFFFFFF


def fnv1a_hash(key: Hashable) -> int:
    data = repr(key).encode("utf-8")
    h = _FNV_OFFSET_BASIS
    for b in data:
        h ^= b
        h = (h * _FNV_PRIME) & _MASK_32
    return h


class _Entry(Generic[K, V]):
    __slots__ = ("key", "value")

    def __init__(self, key: K, value: V):
        self.key = key
        self.value = value


class HashTable(Generic[K, V]):
    MAX_LOAD_FACTOR = 0.75
    MIN_CAPACITY = 8

    def __init__(self, capacity: int = MIN_CAPACITY):
        capacity = max(capacity, self.MIN_CAPACITY)
        self._capacity = capacity
        self._buckets: list[list[_Entry[K, V]]] = [[] for _ in range(capacity)]
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    @property
    def load_factor(self) -> float:
        return self._size / self._capacity

    def _bucket_index(self, key: K) -> int:
        return fnv1a_hash(key) % self._capacity

    def put(self, key: K, value: V) -> None:
        idx = self._bucket_index(key)
        for entry in self._buckets[idx]:
            if entry.key == key:
                entry.value = value
                return
        self._buckets[idx].append(_Entry(key, value))
        self._size += 1
        if self.load_factor > self.MAX_LOAD_FACTOR:
            self._resize(self._capacity * 2)

    def get(self, key: K, default: V | None = None) -> V | None:
        idx = self._bucket_index(key)
        for entry in self._buckets[idx]:
            if entry.key == key:
                return entry.value
        return default

    def __contains__(self, key: K) -> bool:
        idx = self._bucket_index(key)
        return any(entry.key == key for entry in self._buckets[idx])

    def delete(self, key: K) -> V:
        idx = self._bucket_index(key)
        bucket = self._buckets[idx]
        for i, entry in enumerate(bucket):
            if entry.key == key:
                del bucket[i]
                self._size -= 1
                return entry.value
        raise KeyError(key)

    def keys(self) -> Iterator[K]:
        for bucket in self._buckets:
            for entry in bucket:
                yield entry.key

    def values(self) -> Iterator[V]:
        for bucket in self._buckets:
            for entry in bucket:
                yield entry.value

    def items(self) -> Iterator[tuple[K, V]]:
        for bucket in self._buckets:
            for entry in bucket:
                yield (entry.key, entry.value)

    def _resize(self, new_capacity: int) -> None:
        old_entries = [entry for bucket in self._buckets for entry in bucket]
        self._capacity = new_capacity
        self._buckets = [[] for _ in range(new_capacity)]
        for entry in old_entries:
            idx = self._bucket_index(entry.key)
            self._buckets[idx].append(entry)

    def max_chain_length(self) -> int:
        """Diagnostic: longest bucket chain (bounds worst-case lookup cost)."""
        return max((len(b) for b in self._buckets), default=0)
