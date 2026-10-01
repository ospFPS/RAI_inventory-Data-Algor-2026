def merge(left, right, key_func, reverse=False):
    sorted_items = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        left_key = key_func(left[i])
        right_key = key_func(right[j])

        if reverse:
            take_left = left_key >= right_key
        else:
            take_left = left_key <= right_key

        if take_left:
            sorted_items.append(left[i])
            i += 1
        else:
            sorted_items.append(right[j])
            j += 1

    while i < len(left):
        sorted_items.append(left[i])
        i += 1

    while j < len(right):
        sorted_items.append(right[j])
        j += 1

    return sorted_items


def merge_sort(items, key_func=lambda item: item, reverse=False):
    if len(items) <= 1:
        return list(items)

    middle = len(items) // 2

    left = merge_sort(
        items[:middle],
        key_func,
        reverse
    )

    right = merge_sort(
        items[middle:],
        key_func,
        reverse
    )

    return merge(
        left,
        right,
        key_func,
        reverse
    )
