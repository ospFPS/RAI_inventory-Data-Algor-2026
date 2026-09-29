"""Naive baselines to benchmark the hand-implemented structures against
(section 11 of the brief). These are *not* graded DSA structures -- just
straightforward reference implementations so the comparison numbers mean
something. Where the brief names a real structure as the baseline
("array/linked list lookup"), we reuse the real one (ds/linkedlist.py)
instead of writing a redundant stand-in.
"""

from algo.binary_search import lower_bound
from benchmarks.counters import Counted, Counter
from ds.linkedlist import SinglyLinkedList


# -- unsorted array: O(1) insert, O(n) find-min -----------------------


def unsorted_array_insert(arr: list, value, counter: Counter) -> None:
    arr.append(value)  # O(1), no comparisons


def unsorted_array_find_min(arr: list, counter: Counter):
    best = arr[0]
    for v in arr[1:]:
        if Counted(v, counter) < best:
            best = v
    return best


# -- sorted array: O(log n) + O(n) shifts insert, O(1) find-min --------


def sorted_array_insert(arr: list, value, counter: Counter) -> None:
    idx = lower_bound(arr, value, key_func=lambda x: Counted(x, counter))
    arr.insert(idx, value)
    counter.shifts += len(arr) - 1 - idx  # elements shifted right by one


def sorted_array_find_min(arr: list, counter: Counter):
    return arr[0]  # O(1), no comparisons


# -- lookup baselines for the hash table comparison ---------------------


def linear_list_lookup(pairs: list[tuple], target_key, counter: Counter):
    for key, value in pairs:
        if Counted(key, counter) == target_key:
            return value
    return None


def linked_list_lookup(ll: SinglyLinkedList, target_key, counter: Counter):
    for key, value in ll.traverse():
        if Counted(key, counter) == target_key:
            return value
    return None


def hashtable_probe_lookup(table, key) -> tuple[object | None, int]:
    """Mirrors what HashTable.get() does internally, but counts how many
    chain entries were checked (probes) along the way. Reads the table's
    own bucket layout rather than reimplementing hashing/resize."""
    idx = table._bucket_index(key)
    bucket = table._buckets[idx]
    probes = 0
    for entry in bucket:
        probes += 1
        if entry.key == key:
            return entry.value, probes
    return None, probes


# -- linear search baseline for the binary search comparison ------------


def linear_search(arr: list, target, counter: Counter, key_func=lambda x: x) -> int:
    for i, item in enumerate(arr):
        if Counted(key_func(item), counter) == target:
            return i
    return -1


# -- reference sorts for the merge sort comparison -----------------------


def bubble_sort(arr: list, counter: Counter) -> list:
    arr = list(arr)
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if Counted(arr[j], counter) > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def selection_sort(arr: list, counter: Counter) -> list:
    arr = list(arr)
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if Counted(arr[j], counter) < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


def insertion_sort(arr: list, counter: Counter) -> list:
    arr = list(arr)
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and Counted(arr[j], counter) > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


def quicksort(arr: list, counter: Counter) -> list:
    arr = list(arr)
    _quicksort(arr, 0, len(arr) - 1, counter)
    return arr


def _quicksort(arr: list, lo: int, hi: int, counter: Counter) -> None:
    if lo >= hi:
        return
    pivot = arr[hi]
    i = lo - 1
    for j in range(lo, hi):
        if Counted(arr[j], counter) <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
    _quicksort(arr, lo, i, counter)
    _quicksort(arr, i + 2, hi, counter)
