import random
from dataclasses import dataclass

from algo.merge_sort import merge_sort


def test_sorts_ints_ascending():
    arr = [5, 3, 8, 1, 9, 2, 7]
    assert merge_sort(arr) == sorted(arr)
    # original list is untouched
    assert arr == [5, 3, 8, 1, 9, 2, 7]


def test_sorts_descending_with_reverse():
    arr = [5, 3, 8, 1, 9, 2, 7]
    assert merge_sort(arr, reverse=True) == sorted(arr, reverse=True)


def test_empty_and_singleton():
    assert merge_sort([]) == []
    assert merge_sort([42]) == [42]


def test_key_func():
    words = ["banana", "fig", "apple", "kiwi"]
    assert merge_sort(words, key_func=len) == sorted(words, key=len)


@dataclass
class Request:
    project: str
    pick_up_date: str
    submitted_at: str


def test_stability_equal_keys_keep_insertion_order():
    # Same pick_up_date -> merge sort must preserve submission order.
    requests = [
        Request("P1", "2026-01-05", "09:00"),
        Request("P2", "2026-01-05", "09:00"),
        Request("P3", "2026-01-01", "10:00"),
        Request("P4", "2026-01-05", "09:00"),
    ]
    result = merge_sort(requests, key_func=lambda r: r.pick_up_date)
    same_date = [r.project for r in result if r.pick_up_date == "2026-01-05"]
    assert same_date == ["P1", "P2", "P4"]


def test_randomized_matches_python_sorted_oracle():
    random.seed(11)
    for _ in range(30):
        n = random.randint(0, 60)
        arr = [random.randint(-50, 50) for _ in range(n)]
        assert merge_sort(arr) == sorted(arr)
