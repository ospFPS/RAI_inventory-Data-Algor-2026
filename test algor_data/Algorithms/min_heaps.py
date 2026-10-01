from pathlib import Path
import sys

TEST_ROOT = Path(__file__).resolve().parents[1]
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))

from Models.project import Project


class MinHeap:

    def __init__(self):
        self.heap = []

    def is_higher_priority(self, project1, project2):
        if project1.pickup_date < project2.pickup_date:
            return True
        if project1.pickup_date > project2.pickup_date:
            return False
        return project1.request_order < project2.request_order

    def insert(self, project):
        self.heap.append(project)
        self._heapify_up(len(self.heap) - 1)

    def _heapify_up(self, index):
        while index > 0:
            parent = (index - 1) // 2

            if self.is_higher_priority(
                self.heap[index],
                self.heap[parent]
            ):
                self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
                index = parent
            else:
                break

    def extract_min(self):
        if len(self.heap) == 0:
            return None

        min_project = self.heap[0]
        last_project = self.heap.pop()

        if len(self.heap) > 0:
            self.heap[0] = last_project
            self._heapify_down(0)

        return min_project

    def remove_project(self, project_id):
        for i in range(len(self.heap)):

            if self.heap[i].project_id == project_id:
                removed_project = self.heap[i]
                last_project = self.heap.pop()

                if i < len(self.heap):
                    self.heap[i] = last_project

                    if i > 0:
                        parent = (i - 1) // 2

                        if self.is_higher_priority(
                            self.heap[i],
                            self.heap[parent]
                        ):
                            self._heapify_up(i)
                        else:
                            self._heapify_down(i)
                    else:
                        self._heapify_down(i)

                return removed_project

        return None

    def _heapify_down(self, index):
        size = len(self.heap)

        while True:
            left = 2 * index + 1
            right = 2 * index + 2
            smallest = index

            if left < size and self.is_higher_priority(
                self.heap[left],
                self.heap[smallest]
            ):
                smallest = left

            if right < size and self.is_higher_priority(
                self.heap[right],
                self.heap[smallest]
            ):
                smallest = right

            if smallest == index:
                break

            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            index = smallest

    def is_empty(self):
        return len(self.heap) == 0

    def size(self):
        return len(self.heap)

    def display(self):
        if self.is_empty():
            print("Heap is empty.")
            return

        for project in self.heap:
            print(project)


class ProjectManager:

    def __init__(self, main_heap):
        self.main_heap = main_heap
        self.next_project_number = 1
        self.next_request_order = 1

    def submit_request(
        self,
        student_id,
        student_name,
        project_name,
        student_email,
        pickup_date,
        items
    ):
        project_id = f"P{self.next_project_number:04d}"
        request_order = self.next_request_order

        project = Project(
            project_id,
            student_id,
            student_name,
            project_name,
            student_email,
            pickup_date,
            items,
            request_order
        )

        self.main_heap.insert(project)

        self.next_project_number += 1
        self.next_request_order += 1

        return project


def check_availability(project, inventory):
    for item_name, quantity in project.items.items():

        if item_name not in inventory:
            return False

        if inventory[item_name] < quantity:
            return False

    return True


def show_shortage(project, inventory):
    for item_name, quantity in project.items.items():
        current_stock = inventory.get(item_name, 0)

        if current_stock < quantity:
            print(
                item_name,
                "need",
                quantity,
                "have",
                current_stock,
                "short by",
                quantity - current_stock
            )


def borrow_items(project, inventory):
    for item_name, quantity in project.items.items():
        inventory[item_name] -= quantity


def process_main(main_heap, pending_heap, inventory):
    print("\nProcessing Main Min-Heap:")

    while not main_heap.is_empty():
        project = main_heap.extract_min()

        print("\nChecking:")
        print(project)

        if check_availability(project, inventory):
            borrow_items(project, inventory)
            project.status = "BORROWED"

            print("Items are available.")
            print("Status:", project.status)
        else:
            project.status = "PENDING"
            pending_heap.insert(project)

            print("Items are not available.")
            show_shortage(project, inventory)
            print("Moved to Pending Min-Heap.")


def process_pending(pending_heap, inventory):
    if pending_heap.is_empty():
        print("Pending Heap is empty.")
        return None

    best_project = None

    for project in pending_heap.heap:

        if check_availability(project, inventory):

            if best_project is None:
                best_project = project

            elif pending_heap.is_higher_priority(
                project,
                best_project
            ):
                best_project = project

    if best_project is None:
        print("No pending project can be fulfilled yet.")
        return None

    pending_heap.remove_project(best_project.project_id)
    borrow_items(best_project, inventory)
    best_project.status = "BORROWED"

    print("Selected from Pending:")
    print(best_project)

    return best_project


# Main queue
main_heap = MinHeap()

# Pending queue
pending_heap = MinHeap()

project_manager = ProjectManager(main_heap)


# Real item names and quantities read from data/app.db.
inventory = {
    "Form2 3D Printer": 1,
    "Wireless HDMI Extender Kits": 2,
    "Screw driver set": 419
}


# For testing
# P0001 has the earliest pickup date, but does not have enough stock.
p1 = project_manager.submit_request(
    "66000001",
    "Alice",
    "3D Printing Project",
    "alice@example.com",
    "2026-10-02",
    {"Form2 3D Printer": 4}
)

# P0002 and P0003 have the same pickup date.
# P0002 was submitted first, so it has higher priority than P0003.
p2 = project_manager.submit_request(
    "66000002",
    "Bob",
    "Wireless Display Project",
    "bob@example.com",
    "2026-10-03",
    {"Wireless HDMI Extender Kits": 1}
)

p3 = project_manager.submit_request(
    "66000003",
    "Charlie",
    "Workshop Project",
    "charlie@example.com",
    "2026-10-03",
    {"Screw driver set": 2}
)

# P0004 also needs Form2 printers and will enter Pending.
p4 = project_manager.submit_request(
    "66000004",
    "David",
    "3D Scan and Print Project",
    "david@example.com",
    "2026-10-05",
    {"Form2 3D Printer": 3}
)


print("Original Inventory:")
for item_name, quantity in inventory.items():
    print(item_name, "=", quantity)


print("\nMain Min-Heap before processing:")
main_heap.display()


process_main(
    main_heap,
    pending_heap,
    inventory
)


print("\nInventory after Main Heap processing:")
for item_name, quantity in inventory.items():
    print(item_name, "=", quantity)


print("\nPending Min-Heap:")
pending_heap.display()


# Simulate returned stock.
print("\n2 Form2 3D Printers returned to inventory.")
inventory["Form2 3D Printer"] += 2
print("Form2 3D Printer =", inventory["Form2 3D Printer"])


print("\nRe-checking Pending Min-Heap:")
process_pending(
    pending_heap,
    inventory
)


print("\nRemaining Pending Projects:")
pending_heap.display()


print("\nInventory after first Pending check:")
for item_name, quantity in inventory.items():
    print(item_name, "=", quantity)


# P0001 is still waiting because it needs 4 printers.
# Add 4 printers so it can now be fulfilled.
print("\n4 more Form2 3D Printers returned to inventory.")
inventory["Form2 3D Printer"] += 4
print("Form2 3D Printer =", inventory["Form2 3D Printer"])


print("\nRe-checking Pending Min-Heap again:")
process_pending(
    pending_heap,
    inventory
)


print("\nFinal Pending Min-Heap:")
pending_heap.display()


print("\nFinal Inventory:")
for item_name, quantity in inventory.items():
    print(item_name, "=", quantity)
