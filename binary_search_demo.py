"""Standalone demonstration of the hand-implemented binary search
(algo/binary_search.py) against mock data, proving correctness by
comparing it to a trivial linear-scan oracle -- no pytest required,
just run it and read the output.

Run:
    python binary_search_demo.py
"""

import random

from algo.binary_search import (
    binary_search_exact,
    lower_bound,
    prefix_search,
    upper_bound,
)


def section(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def linear_search_oracle(arr, target, key_func=lambda x: x):
    """Dumb O(n) reference implementation: scan everything. Used only
    to prove the binary search results are correct, never in the app."""
    for i, item in enumerate(arr):
        if key_func(item) == target:
            return i
    return -1


# -- mock data ---------------------------------------------------------
# A small slice of RAI-style inventory, already sorted by (type, name)
# the same way app/inventory.py keeps the real catalog sorted.
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
# NB: sorted by type then name to match binary search's precondition --
# double check that assumption instead of just trusting it.
assert MOCK_CATALOG == sorted(MOCK_CATALOG), "mock data must be pre-sorted"


def demo_exact_hits_and_misses():
    section("1. Exact lookup: hits and misses")
    targets = [
        ("Sensor", "Ultrasonic Sensor HC-SR04"),  # present, middle-ish
        ("Control", "Arduino Mega 2560"),           # present, first element
        ("Sensor", "Ultrasonic Sensor HC-SR05"),    # present, last element
        ("Sensor", "LIDAR Module"),                 # absent (sorts into Sensor range)
        ("Zzz", "Nonexistent Type"),                # absent (past the end)
    ]
    for target in targets:
        got = binary_search_exact(MOCK_CATALOG, target)
        want = linear_search_oracle(MOCK_CATALOG, target)
        status = "PASS" if got == want else "FAIL"
        found_desc = f"found at index {got}" if got != -1 else "not found (-1)"
        print(f"  [{status}] search({target!r}) -> {found_desc}")
        assert got == want, f"mismatch vs oracle: binary={got} oracle={want}"


def demo_empty_and_singleton():
    section("2. Edge cases: empty array and single element")
    empty: list = []
    assert binary_search_exact(empty, ("Any", "Thing")) == -1
    print("  [PASS] empty array always returns -1")

    single = [("Control", "Arduino Uno R3")]
    assert binary_search_exact(single, ("Control", "Arduino Uno R3")) == 0
    assert binary_search_exact(single, ("Control", "Other")) == -1
    print("  [PASS] single-element array: hit and miss both correct")


def demo_lower_upper_bound():
    section("3. lower_bound / upper_bound on a list with duplicates")
    arr = [1, 3, 3, 3, 5, 7, 9]
    print(f"  array: {arr}")
    lo = lower_bound(arr, 3)
    hi = upper_bound(arr, 3)
    print(f"  lower_bound(3) = {lo}  (first index where value >= 3)")
    print(f"  upper_bound(3) = {hi}  (first index where value >  3)")
    assert arr[lo:hi] == [3, 3, 3]
    print(f"  [PASS] arr[{lo}:{hi}] = {arr[lo:hi]} -- exactly the three 3's")

    assert lower_bound(arr, 0) == 0
    assert lower_bound(arr, 100) == len(arr)
    print("  [PASS] lower_bound below range -> 0, above range -> len(arr)")


def demo_prefix_search():
    section("4. prefix_search: the component search-box use case")
    queries = ["Ultrasonic", "Relay", "Arduino", "Nope"]
    for q in queries:
        results = prefix_search(MOCK_CATALOG, q, key_func=lambda item: item[1])
        names = [item[1] for item in results]
        print(f"  prefix_search({q!r:15s}) -> {names}")
        # cross-check against a plain linear filter
        expected = [item[1] for item in MOCK_CATALOG if item[1].startswith(q)]
        assert names == expected, f"mismatch: {names} != {expected}"
    print("  [PASS] every prefix query matches a linear str.startswith() filter")


def demo_randomized_stress_test(trials=200, max_size=60):
    section(f"5. Randomized stress test ({trials} trials vs linear-search oracle)")
    random.seed(42)
    failures = 0
    for _ in range(trials):
        n = random.randint(0, max_size)
        arr = sorted(random.sample(range(-500, 500), n))
        # mix of present and absent targets
        target = random.choice(arr) if arr and random.random() < 0.5 else random.randint(-600, 600)
        got = binary_search_exact(arr, target)
        want = linear_search_oracle(arr, target)
        ok = (got == -1 and want == -1) or (got != -1 and arr[got] == target)
        if not ok:
            failures += 1
            print(f"  [FAIL] arr={arr} target={target} got={got}")
    if failures == 0:
        print(f"  [PASS] all {trials} random trials matched the oracle")
    else:
        print(f"  [FAIL] {failures}/{trials} trials mismatched")
    assert failures == 0


def main():
    print("Binary Search Demonstration (algo/binary_search.py)")
    print("Proving correctness against mock data and a linear-search oracle.")
    demo_exact_hits_and_misses()
    demo_empty_and_singleton()
    demo_lower_upper_bound()
    demo_prefix_search()
    demo_randomized_stress_test()
    section("All binary search demonstrations passed.")


if __name__ == "__main__":
    main()
