from pathlib import Path
import sys

TEST_ROOT = Path(__file__).resolve().parents[1]
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))

from mock_data import load_mock_items


def binary_search(inventory, item_type, item_name):
    left = 0
    right = len(inventory) - 1
    checks = 0

    target = (
        item_type.lower(),
        item_name.lower()
    )

    while left <= right:
        middle = (left + right) // 2
        checks += 1

        current = (
            inventory[middle].item_type.lower(),
            inventory[middle].item_name.lower()
        )

        if current == target:
            return inventory[middle], checks

        if current < target:
            left = middle + 1
        else:
            right = middle - 1

    return None, checks


# The search demo uses all real Excel inventory rows copied into mock memory.
inventory = sorted(
    load_mock_items(),
    key=lambda item: (item.item_type.lower(), item.item_name.lower())
)

print(f"Excel-backed mock inventory: {len(inventory)} items")
for item in inventory[:12]:
    print(item)
print("... (showing first 12; all items are searchable)")


item_type = input("\nEnter item type: ")
item_name = input("Enter item name: ")

print(
    "\nSearching for:",
    item_type,
    "-",
    item_name
)

result, checks = binary_search(
    inventory,
    item_type,
    item_name
)

if result is not None:
    print("Item found:")
    print(result)
    print("Binary Search checks:", checks)
else:
    print("Item not found.")
    print("Binary Search checks:", checks)


# Test an item that does not exist.
print("\nSearching for an item that does not exist:")

result, checks = binary_search(
    inventory,
    "Tool",
    "Item That Does Not Exist"
)

if result is not None:
    print(result)
else:
    print("Item not found.")
    print("Binary Search checks:", checks)
