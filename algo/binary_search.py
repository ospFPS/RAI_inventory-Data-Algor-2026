"""Hand-implemented binary search over a sorted array.

The inventory is kept sorted by (type, item_name) so that all lookups
here run in O(log m) instead of the O(m) an unsorted linear scan (or a
binary search *tree* with no balance guarantee) would cost. For m ~ 200
items, log2(200) ~= 7.6, i.e. about 8 comparisons worst case, matching
the brief's target.

Three operations, all O(log m):
    binary_search_exact -- index of a key equal to target, or -1
    lower_bound          -- first index whose key is >= target
    upper_bound          -- first index whose key is >  target

lower_bound/upper_bound together give an O(log m + k) prefix search
(k = number of matches): find the [lower_bound(prefix), upper_bound(prefix
+ '\\uffff')) slice instead of scanning every item.
"""

from typing import Callable, TypeVar

T = TypeVar("T")
K = TypeVar("K")


def binary_search_exact(
    arr: list[T], target: K, key_func: Callable[[T], K] = lambda x: x
) -> int:
    """Return the index of an element whose key == target, else -1.

    ``arr`` must already be sorted ascending by ``key_func``.
    """
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        mid_key = key_func(arr[mid])
        if mid_key == target:
            return mid
        if mid_key < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def lower_bound(
    arr: list[T], target: K, key_func: Callable[[T], K] = lambda x: x
) -> int:
    """First index i such that key_func(arr[i]) >= target (len(arr) if none)."""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if key_func(arr[mid]) < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def upper_bound(
    arr: list[T], target: K, key_func: Callable[[T], K] = lambda x: x
) -> int:
    """First index i such that key_func(arr[i]) > target (len(arr) if none)."""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if key_func(arr[mid]) <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo


def prefix_search(
    arr: list[T], prefix: str, key_func: Callable[[T], str] = lambda x: x
) -> list[T]:
    """All elements whose string key starts with ``prefix``, in O(log m + k).

    ``arr`` must be sorted ascending by ``key_func``.
    """
    if prefix == "":
        return list(arr)
    lo = lower_bound(arr, prefix, key_func)
    hi = upper_bound(arr, prefix + "￿", key_func)
    return arr[lo:hi]
