"""Hand-implemented merge sort.

Used for the admin's ordered request view. O(n log n) in every case
(best, average, worst) unlike quicksort's O(n^2) worst case, and stable
(equal-key items keep their relative order) unlike selection/quick sort,
which matters here: requests with the same pick-up date should stay in
submission order.

Complexity: T(n) = 2T(n/2) + O(n) (split in half, merge two sorted
halves in linear time) => O(n log n) time, O(n) auxiliary space.
"""

from typing import Callable, TypeVar

T = TypeVar("T")
K = TypeVar("K")


def merge_sort(
    arr: list[T], key_func: Callable[[T], K] = lambda x: x, reverse: bool = False
) -> list[T]:
    """Return a new list containing ``arr``'s elements in ascending key order."""
    n = len(arr)
    if n <= 1:
        return list(arr)
    mid = n // 2
    left = merge_sort(arr[:mid], key_func, reverse)
    right = merge_sort(arr[mid:], key_func, reverse)
    return _merge(left, right, key_func, reverse)


def _merge(
    left: list[T], right: list[T], key_func: Callable[[T], K], reverse: bool
) -> list[T]:
    merged: list[T] = []
    i = j = 0
    while i < len(left) and j < len(right):
        take_left = key_func(left[i]) <= key_func(right[j])
        if reverse:
            take_left = key_func(left[i]) >= key_func(right[j])
        if take_left:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged
