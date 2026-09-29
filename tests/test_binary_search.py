import random

from algo.binary_search import (
    binary_search_exact,
    lower_bound,
    prefix_search,
    upper_bound,
)


def make_inventory():
    # Sorted by (type, item_name), matching how the app keeps the catalog.
    return [
        ("Control", "Arduino Uno"),
        ("Control", "Raspberry Pi 4"),
        ("Electrical", "Relay 12V"),
        ("Electrical", "Relay 5V"),
        ("Electrical", "Resistor 220R"),
        ("Mechanical", "Bearing 608ZZ"),
        ("Sensor", "IR Sensor"),
        ("Sensor", "Ultrasonic HC-SR04"),
        ("Sensor", "Ultrasonic HC-SR05"),
    ]


def test_exact_hit():
    arr = make_inventory()
    idx = binary_search_exact(arr, ("Sensor", "IR Sensor"))
    assert arr[idx] == ("Sensor", "IR Sensor")


def test_exact_miss():
    arr = make_inventory()
    assert binary_search_exact(arr, ("Sensor", "Nonexistent")) == -1


def test_exact_empty_array():
    assert binary_search_exact([], ("a", "b")) == -1


def test_exact_first_and_last_element():
    arr = make_inventory()
    assert arr[binary_search_exact(arr, arr[0])] == arr[0]
    assert arr[binary_search_exact(arr, arr[-1])] == arr[-1]


def test_lower_upper_bound_basic():
    arr = [1, 3, 3, 3, 5, 7]
    assert lower_bound(arr, 3) == 1
    assert upper_bound(arr, 3) == 4
    assert lower_bound(arr, 0) == 0
    assert lower_bound(arr, 8) == len(arr)
    assert upper_bound(arr, 8) == len(arr)


def test_prefix_search_matches_names():
    items = [
        {"name": "Relay 12V"},
        {"name": "Relay 5V"},
        {"name": "Resistor 220R"},
        {"name": "Ultrasonic HC-SR04"},
    ]
    result = prefix_search(items, "Relay", key_func=lambda x: x["name"])
    assert [r["name"] for r in result] == ["Relay 12V", "Relay 5V"]


def test_prefix_search_no_match():
    items = [{"name": "Relay 12V"}, {"name": "Resistor 220R"}]
    assert prefix_search(items, "ZZZ", key_func=lambda x: x["name"]) == []


def test_prefix_search_empty_prefix_returns_all():
    items = [{"name": "A"}, {"name": "B"}]
    assert prefix_search(items, "", key_func=lambda x: x["name"]) == items


def test_randomized_matches_linear_search_oracle():
    random.seed(3)
    for _ in range(30):
        n = random.randint(0, 40)
        arr = sorted(random.sample(range(-100, 100), n))
        target = random.randint(-110, 110)
        expected = arr.index(target) if target in arr else -1
        got = binary_search_exact(arr, target)
        if expected == -1:
            assert got == -1
        else:
            assert arr[got] == target
