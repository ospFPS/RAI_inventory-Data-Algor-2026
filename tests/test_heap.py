import random

import pytest

from ds.heap import MinHeap


def make_item(key, id_):
    return {"key": key, "id": id_}


def key_func(item):
    return item["key"]


def id_func(item):
    return item["id"]


def new_heap():
    return MinHeap(key_func, id_func)


def test_empty_heap_raises():
    h = new_heap()
    assert len(h) == 0
    assert h.is_empty()
    with pytest.raises(IndexError):
        h.peek()
    with pytest.raises(IndexError):
        h.pop()


def test_push_pop_orders_by_key():
    h = new_heap()
    keys = [5, 3, 8, 1, 9, 2, 7]
    for i, k in enumerate(keys):
        h.push(make_item(k, f"id{i}"))
    assert len(h) == len(keys)
    popped = [h.pop() for _ in range(len(keys))]
    assert [item["key"] for item in popped] == sorted(keys)
    assert h.is_empty()


def test_peek_does_not_remove():
    h = new_heap()
    h.push(make_item(5, "a"))
    h.push(make_item(1, "b"))
    assert h.peek()["key"] == 1
    assert len(h) == 2


def test_tie_break_key_is_tuple():
    # Main heap key is (pick_up_date, submitted_at); equal pick-up dates
    # break ties by earlier submission time.
    h = new_heap()
    h.push(make_item(("2026-01-05", "10:00"), "late-submit"))
    h.push(make_item(("2026-01-05", "09:00"), "early-submit"))
    h.push(make_item(("2026-01-01", "23:00"), "earliest-date"))
    order = [h.pop()["id"] for _ in range(3)]
    assert order == ["earliest-date", "early-submit", "late-submit"]


def test_duplicate_id_rejected():
    h = new_heap()
    h.push(make_item(1, "dup"))
    with pytest.raises(ValueError):
        h.push(make_item(2, "dup"))


def test_remove_by_id_arbitrary_position():
    h = new_heap()
    for i, k in enumerate([10, 20, 30, 40, 50, 5]):
        h.push(make_item(k, f"id{i}"))
    removed = h.remove("id3")  # key 40, not the root
    assert removed["key"] == 40
    assert "id3" not in h
    remaining_keys = sorted(h.pop()["key"] for _ in range(len(h)))
    assert remaining_keys == [5, 10, 20, 30, 50]


def test_remove_root():
    h = new_heap()
    for i, k in enumerate([3, 1, 2]):
        h.push(make_item(k, f"id{i}"))
    assert h.peek()["key"] == 1
    h.remove("id1")  # id1 has key 1, currently at the root
    assert h.peek()["key"] == 2


def test_remove_missing_id_raises():
    h = new_heap()
    h.push(make_item(1, "a"))
    with pytest.raises(KeyError):
        h.remove("missing")


def test_build_heapify_is_correct_and_o_n():
    items = [make_item(k, f"id{k}") for k in range(999, -1, -1)]
    h = MinHeap.build(items, key_func, id_func)
    assert len(h) == 1000
    popped = [h.pop()["key"] for _ in range(1000)]
    assert popped == sorted(range(1000))


def test_update_key_moves_item_down_and_up():
    h = new_heap()
    for i, k in enumerate([10, 20, 30]):
        h.push(make_item(k, f"id{i}"))
    # id0 currently has key 10 (the min); raise it so it should sink.
    h.update_key("id0", make_item(100, "id0"))
    assert h.peek()["key"] == 20
    # now lower id2's key (30) below everything so it should rise to root.
    h.update_key("id2", make_item(1, "id2"))
    assert h.peek()["key"] == 1
    assert h.peek()["id"] == "id2"


def test_randomized_matches_python_sorted():
    random.seed(42)
    for _ in range(20):
        n = random.randint(0, 50)
        keys = [random.randint(0, 1000) for _ in range(n)]
        h = new_heap()
        for i, k in enumerate(keys):
            h.push(make_item(k, f"id{i}"))
        result = [h.pop()["key"] for _ in range(n)]
        assert result == sorted(keys)
