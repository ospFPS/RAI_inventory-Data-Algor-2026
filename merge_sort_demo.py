"""Standalone demonstration of the hand-implemented merge sort
(algo/merge_sort.py) against mock data, proving correctness by
comparing it to Python's built-in sorted() as an oracle, and proving
stability (the property the admin priority view actually depends on)
with a scenario that mirrors real project requests.

Run:
    python merge_sort_demo.py
"""

import random
from dataclasses import dataclass

from algo.merge_sort import merge_sort


def section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def demo_basic_numbers():
    section("1. Basic correctness: unsorted numbers vs sorted() oracle")
    mock_data = [42, 7, 19, 3, 56, 1, 23, 8, 91, 4]
    print(f"  input:    {mock_data}")

    result = merge_sort(mock_data)
    expected = sorted(mock_data)
    print(f"  output:   {result}")
    print(f"  expected: {expected}")

    assert result == expected
    assert mock_data == [42, 7, 19, 3, 56, 1, 23, 8, 91, 4], "must not mutate the input"
    print("  [PASS] sorted correctly, and the original list was left untouched")


def demo_descending_and_key_func():
    section("2. reverse=True and a custom key_func")
    words = ["banana", "fig", "kiwi", "apple", "watermelon", "pear"]
    print(f"  input: {words}")

    by_length = merge_sort(words, key_func=len)
    print(f"  sorted by len(word), ascending: {by_length}")
    assert by_length == sorted(words, key=len)

    by_length_desc = merge_sort(words, key_func=len, reverse=True)
    print(f"  sorted by len(word), descending: {by_length_desc}")
    assert by_length_desc == sorted(words, key=len, reverse=True)
    print("  [PASS] both ascending and descending key-based sorts match sorted()")


def demo_edge_cases():
    section("3. Edge cases: empty, single element, already sorted, all-equal")
    assert merge_sort([]) == []
    print("  [PASS] empty list -> empty list")

    assert merge_sort([99]) == [99]
    print("  [PASS] single element -> unchanged")

    already = [1, 2, 3, 4, 5]
    assert merge_sort(already) == already
    print("  [PASS] already-sorted input stays sorted")

    all_equal = [5, 5, 5, 5, 5]
    assert merge_sort(all_equal) == all_equal
    print("  [PASS] all-equal elements handled fine")


def demo_stability():
    section("4. Stability: the property the Admin Priority View relies on")

    @dataclass
    class MockRequest:
        project_id: str
        pick_up_date: str
        submitted_at: str

        def __repr__(self):
            return f"{self.project_id}(date={self.pick_up_date}, t={self.submitted_at})"

    # Three requests share the SAME pick-up date; a stable sort must
    # keep them in submission order (P1 submitted before P2 before P4).
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
    print(f"  requests sharing 2026-01-05, in output order: {same_date_ids}")
    assert same_date_ids == ["P1", "P2", "P4"], "stability violated: submission order not preserved"
    assert result[0].project_id == "P3", "earliest pick-up date should sort first"
    print("  [PASS] equal-key items kept their original relative order (stable)")
    print("  [PASS] earliest pick-up date correctly sorted to the front")


def demo_randomized_stress_test(trials=200, max_size=80):
    section(f"5. Randomized stress test ({trials} trials vs sorted() oracle)")
    random.seed(2026)
    failures = 0
    for _ in range(trials):
        n = random.randint(0, max_size)
        arr = [random.randint(-1000, 1000) for _ in range(n)]
        got = merge_sort(arr)
        want = sorted(arr)
        if got != want:
            failures += 1
            print(f"  [FAIL] input={arr}")
            print(f"         got ={got}")
            print(f"         want={want}")
    if failures == 0:
        print(f"  [PASS] all {trials} random trials matched sorted()")
    else:
        print(f"  [FAIL] {failures}/{trials} trials mismatched")
    assert failures == 0


def main():
    print("Merge Sort Demonstration (algo/merge_sort.py)")
    print("Proving correctness against mock data and Python's sorted() oracle,")
    print("plus the stability guarantee the admin priority view depends on.")
    demo_basic_numbers()
    demo_descending_and_key_func()
    demo_edge_cases()
    demo_stability()
    demo_randomized_stress_test()
    section("All merge sort demonstrations passed.")


if __name__ == "__main__":
    main()
