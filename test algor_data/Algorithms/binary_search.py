from pathlib import Path
import sys

TEST_ROOT = Path(__file__).resolve().parents[1]
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))

from Models.item import Item


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


# For testing
# Real item names and quantities read from data/app.db.
# The list is already sorted by Type and Item Name.
inventory = [
    Item(
        "3D Printer",
        "Form2 3D Printer",
        1
    ),
    Item(
        "3D Printer",
        "Fullscale XT 3D Printer",
        1
    ),
    Item(
        "AV Extender",
        "Wireless HDMI Extender",
        1
    ),
    Item(
        "AV Extender",
        "Wireless HDMI Extender Kits",
        2
    ),
    Item(
        "Sensor",
        "Current Sensor ACS712T ELC-20A",
        16
    ),
    Item(
        "Sensor",
        "Current sensor (ACS712)",
        1
    ),
    Item(
        "Tool",
        "Mini Screw Driver Set",
        13
    ),
    Item(
        "Tool",
        "Screw driver set",
        419
    )
]


print("Inventory:")
for item in inventory:
    print(item)


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
