"""Fully self-contained demonstration of binary search and merge sort.

Unlike binary_search_demo.py / merge_sort_demo.py (which import the
graded implementations from algo/), this single file has NO dependency
on the rest of the repository or any third-party package -- only the
Python standard library. Copy it anywhere and run it on its own:

    python standalone_demo.py

The binary_search_exact/lower_bound/upper_bound/prefix_search and
merge_sort functions below are verbatim copies of algo/binary_search.py
and algo/merge_sort.py in the main project, kept here so this file has
zero external dependencies. The source of truth for the actual
application is algo/, not this copy.
"""

import random
from typing import Callable, TypeVar

T = TypeVar("T")
K = TypeVar("K")


# =====================================================================
# Binary search (verbatim copy of algo/binary_search.py)
# =====================================================================
#
# The inventory is kept sorted by (type, item_name) so that all lookups
# here run in O(log m) instead of the O(m) an unsorted linear scan (or a
# binary search *tree* with no balance guarantee) would cost. For m ~ 200
# items, log2(200) ~= 7.6, i.e. about 8 comparisons worst case.
#
# Three operations, all O(log m):
#   binary_search_exact -- index of a key equal to target, or -1
#   lower_bound          -- first index whose key is >= target
#   upper_bound          -- first index whose key is >  target
#
# lower_bound/upper_bound together give an O(log m + k) prefix search
# (k = number of matches).


def binary_search_exact(
    arr: list[T], target: K, key_func: Callable[[T], K] = lambda x: x
) -> int:
    """Return the index of an element whose key == target, else -1.
    ``arr`` must already be sorted ascending by ``key_func``."""
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
    ``arr`` must be sorted ascending by ``key_func``."""
    if prefix == "":
        return list(arr)
    lo = lower_bound(arr, prefix, key_func)
    hi = upper_bound(arr, prefix + "￿", key_func)
    return arr[lo:hi]


# =====================================================================
# Merge sort (verbatim copy of algo/merge_sort.py)
# =====================================================================
#
# O(n log n) in every case (best, average, worst) unlike quicksort's
# O(n^2) worst case, and stable (equal-key items keep their relative
# order) unlike selection/quick sort.
#
# T(n) = 2T(n/2) + O(n) (split in half, merge two sorted halves in
# linear time) => O(n log n) time, O(n) auxiliary space.


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


# =====================================================================
# Demonstration helpers
# =====================================================================


def section(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def linear_search_oracle(arr, target, key_func=lambda x: x):
    """Dumb O(n) reference: scan everything. Used only to prove binary
    search's results are correct -- never used by the app itself."""
    for i, item in enumerate(arr):
        if key_func(item) == target:
            return i
    return -1


# -- mock data ---------------------------------------------------------

MOCK_CATALOG = [
    ("Control", "Arduino Mega 2560"),
    ("Control", "Arduino Uno R3"),
    ("Control", "ESP32 Dev Board"),
    ("Control", "Raspberry Pi 4 Model B"),
    ("Electrical", "Relay 12V SPDT"),
    ("Electrical", "Relay 5V SPDT"),
    ("Electrical", "Resistor 10K"),
    ("Electrical", "Resistor 220R"),
    ("Mechanical", "Bearing 608ZZ"),
    ("Mechanical", "Timing Belt GT2 1m"),
    ("Sensor", "IR Obstacle Sensor"),
    ("Sensor", "PIR Motion Sensor"),
    ("Sensor", "Ultrasonic Sensor HC-SR04"),
    ("Sensor", "Ultrasonic Sensor HC-SR05"),
]
assert MOCK_CATALOG == sorted(MOCK_CATALOG), "mock data must be pre-sorted"


class MockRequest:
    """Mimics app/models.py's ProjectRequest just enough to demonstrate
    merge sort's stability on the field the admin view actually sorts by."""

    def __init__(self, project_id, pick_up_date, submitted_at):
        self.project_id = project_id
        self.pick_up_date = pick_up_date
        self.submitted_at = submitted_at

    def __repr__(self):
        return f"{self.project_id}(date={self.pick_up_date}, t={self.submitted_at})"


# =====================================================================
# Binary search demonstrations
# =====================================================================


def demo_binary_search_hits_and_misses():
    section("BINARY SEARCH 1: exact lookup, hits and misses")
    targets = [
        ("Sensor", "Ultrasonic Sensor HC-SR04"),  # present, middle-ish
        ("Control", "Arduino Mega 2560"),           # present, first element
        ("Sensor", "Ultrasonic Sensor HC-SR05"),    # present, last element
        ("Sensor", "LIDAR Module"),                 # absent, sorts into Sensor range
        ("Zzz", "Nonexistent Type"),                 # absent, past the end
    ]
    for target in targets:
        got = binary_search_exact(MOCK_CATALOG, target)
        want = linear_search_oracle(MOCK_CATALOG, target)
        status = "PASS" if got == want else "FAIL"
        found_desc = f"found at index {got}" if got != -1 else "not found (-1)"
        print(f"  [{status}] search({target!r}) -> {found_desc}")
        assert got == want


def demo_binary_search_edge_cases():
    section("BINARY SEARCH 2: edge cases (empty, single element)")
    assert binary_search_exact([], ("Any", "Thing")) == -1
    print("  [PASS] empty array always returns -1")

    single = [("Control", "Arduino Uno R3")]
    assert binary_search_exact(single, ("Control", "Arduino Uno R3")) == 0
    assert binary_search_exact(single, ("Control", "Other")) == -1
    print("  [PASS] single-element array: hit and miss both correct")


def demo_binary_search_bounds():
    section("BINARY SEARCH 3: lower_bound / upper_bound on duplicates")
    arr = [1, 3, 3, 3, 5, 7, 9]
    print(f"  array: {arr}")
    lo, hi = lower_bound(arr, 3), upper_bound(arr, 3)
    print(f"  lower_bound(3)={lo}  upper_bound(3)={hi}  -> arr[{lo}:{hi}]={arr[lo:hi]}")
    assert arr[lo:hi] == [3, 3, 3]
    assert lower_bound(arr, 0) == 0 and lower_bound(arr, 100) == len(arr)
    print("  [PASS] duplicates isolated correctly; below/above-range handled")


def demo_binary_search_prefix():
    section("BINARY SEARCH 4: prefix_search (component search-box use case)")
    for q in ["Ultrasonic", "Relay", "Arduino", "Nope"]:
        results = prefix_search(MOCK_CATALOG, q, key_func=lambda item: item[1])
        names = [item[1] for item in results]
        expected = [item[1] for item in MOCK_CATALOG if item[1].startswith(q)]
        print(f"  prefix_search({q!r:15s}) -> {names}")
        assert names == expected
    print("  [PASS] every prefix query matches a linear str.startswith() filter")


def demo_binary_search_stress(trials=200, max_size=60):
    section(f"BINARY SEARCH 5: randomized stress test ({trials} trials)")
    random.seed(42)
    for _ in range(trials):
        n = random.randint(0, max_size)
        arr = sorted(random.sample(range(-500, 500), n))
        target = random.choice(arr) if arr and random.random() < 0.5 else random.randint(-600, 600)
        got = binary_search_exact(arr, target)
        want = linear_search_oracle(arr, target)
        ok = (got == -1 and want == -1) or (got != -1 and arr[got] == target)
        assert ok, f"arr={arr} target={target} got={got}"
    print(f"  [PASS] all {trials} random trials matched the linear-search oracle")


# =====================================================================
# Merge sort demonstrations
# =====================================================================


def demo_merge_sort_basic():
    section("MERGE SORT 1: basic correctness vs sorted() oracle")
    mock_data = [42, 7, 19, 3, 56, 1, 23, 8, 91, 4]
    print(f"  input:    {mock_data}")
    result = merge_sort(mock_data)
    print(f"  output:   {result}")
    assert result == sorted(mock_data)
    assert mock_data == [42, 7, 19, 3, 56, 1, 23, 8, 91, 4], "must not mutate input"
    print("  [PASS] sorted correctly, original list untouched")


def demo_merge_sort_key_and_reverse():
    section("MERGE SORT 2: reverse=True and a custom key_func")
    words = ["banana", "fig", "kiwi", "apple", "watermelon", "pear"]
    print(f"  input: {words}")
    by_len = merge_sort(words, key_func=len)
    by_len_desc = merge_sort(words, key_func=len, reverse=True)
    print(f"  by len(word) ascending:  {by_len}")
    print(f"  by len(word) descending: {by_len_desc}")
    assert by_len == sorted(words, key=len)
    assert by_len_desc == sorted(words, key=len, reverse=True)
    print("  [PASS] both match sorted()")


def demo_merge_sort_edge_cases():
    section("MERGE SORT 3: edge cases (empty, single, sorted, all-equal)")
    assert merge_sort([]) == []
    assert merge_sort([99]) == [99]
    assert merge_sort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]
    assert merge_sort([5, 5, 5, 5, 5]) == [5, 5, 5, 5, 5]
    print("  [PASS] empty / single-element / already-sorted / all-equal all handled")


def demo_merge_sort_stability():
    section("MERGE SORT 4: stability (admin priority view relies on this)")
    mock_requests = [
        MockRequest("P1", "2026-01-05", "09:00"),
        MockRequest("P2", "2026-01-05", "09:05"),
        MockRequest("P3", "2026-01-01", "10:00"),  # earlier date -> sorts first
        MockRequest("P4", "2026-01-05", "09:10"),
    ]
    print("  input (submission order):")
    for r in mock_requests:
        print(f"    {r}")
    result = merge_sort(mock_requests, key_func=lambda r: r.pick_up_date)
    print("  output (sorted by pick_up_date only):")
    for r in result:
        print(f"    {r}")
    same_date_ids = [r.project_id for r in result if r.pick_up_date == "2026-01-05"]
    assert same_date_ids == ["P1", "P2", "P4"], "stability violated"
    assert result[0].project_id == "P3"
    print("  [PASS] equal-key items kept submission order; earliest date sorted first")


def demo_merge_sort_stress(trials=200, max_size=80):
    section(f"MERGE SORT 5: randomized stress test ({trials} trials)")
    random.seed(2026)
    for _ in range(trials):
        n = random.randint(0, max_size)
        arr = [random.randint(-1000, 1000) for _ in range(n)]
        assert merge_sort(arr) == sorted(arr)
    print(f"  [PASS] all {trials} random trials matched sorted()")


def main():
    print("Standalone Binary Search + Merge Sort Demonstration")
    print("(single file, standard library only, no project dependency)")

    demo_binary_search_hits_and_misses()
    demo_binary_search_edge_cases()
    demo_binary_search_bounds()
    demo_binary_search_prefix()
    demo_binary_search_stress()

    demo_merge_sort_basic()
    demo_merge_sort_key_and_reverse()
    demo_merge_sort_edge_cases()
    demo_merge_sort_stability()
    demo_merge_sort_stress()

    section("All demonstrations passed.")


if __name__ == "__main__":
    main()
