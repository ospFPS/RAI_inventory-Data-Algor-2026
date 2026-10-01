def binary_search_exact(inventory, target, key_func=lambda item: item):
    left = 0
    right = len(inventory) - 1

    while left <= right:
        middle = (left + right) // 2
        current = key_func(inventory[middle])

        if current == target:
            return middle

        if current < target:
            left = middle + 1
        else:
            right = middle - 1

    return -1


def lower_bound(inventory, target, key_func=lambda item: item):
    left = 0
    right = len(inventory)

    while left < right:
        middle = (left + right) // 2
        current = key_func(inventory[middle])

        if current < target:
            left = middle + 1
        else:
            right = middle

    return left


def upper_bound(inventory, target, key_func=lambda item: item):
    left = 0
    right = len(inventory)

    while left < right:
        middle = (left + right) // 2
        current = key_func(inventory[middle])

        if current <= target:
            left = middle + 1
        else:
            right = middle

    return left
