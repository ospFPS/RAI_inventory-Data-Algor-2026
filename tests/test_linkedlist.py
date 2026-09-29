from ds.linkedlist import SinglyLinkedList


def test_empty_list():
    ll = SinglyLinkedList()
    assert len(ll) == 0
    assert ll.is_empty()
    assert ll.to_list() == []


def test_append_and_traverse_preserves_order():
    ll = SinglyLinkedList()
    records = ["damage-1", "damage-2", "damage-3"]
    for r in records:
        ll.append(r)
    assert len(ll) == 3
    assert not ll.is_empty()
    assert list(ll.traverse()) == records
    assert ll.to_list() == records


def test_iter_protocol():
    ll = SinglyLinkedList()
    ll.append(1)
    ll.append(2)
    assert [x for x in ll] == [1, 2]


def test_append_many_preserves_o1_tail_semantics():
    ll = SinglyLinkedList()
    n = 1000
    for i in range(n):
        ll.append(i)
    assert len(ll) == n
    assert ll.to_list() == list(range(n))
