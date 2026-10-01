from pathlib import Path
import sys

TEST_ROOT = Path(__file__).resolve().parents[1]
if str(TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_ROOT))

from Models.project import Project


def is_higher_priority(project1, project2):
    if project1.pickup_date < project2.pickup_date:
        return True

    if project1.pickup_date > project2.pickup_date:
        return False

    return project1.request_order < project2.request_order


def merge(left, right):
    sorted_projects = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):

        if is_higher_priority(left[i], right[j]):
            sorted_projects.append(left[i])
            i += 1
        else:
            sorted_projects.append(right[j])
            j += 1

    while i < len(left):
        sorted_projects.append(left[i])
        i += 1

    while j < len(right):
        sorted_projects.append(right[j])
        j += 1

    return sorted_projects


def merge_sort(projects):
    if len(projects) <= 1:
        return projects

    middle = len(projects) // 2

    left = merge_sort(
        projects[:middle]
    )

    right = merge_sort(
        projects[middle:]
    )

    return merge(
        left,
        right
    )


# For testing
# The projects are deliberately not in priority order.
p1 = Project(
    "P0001",
    "66000001",
    "Alice",
    "3D Printing Project",
    "alice@example.com",
    "2026-10-10",
    {"Form2 3D Printer": 1},
    1
)

p2 = Project(
    "P0002",
    "66000002",
    "Bob",
    "Wireless Display Project",
    "bob@example.com",
    "2026-10-05",
    {"Wireless HDMI Extender Kits": 1},
    2
)

p3 = Project(
    "P0003",
    "66000003",
    "Charlie",
    "Workshop Project",
    "charlie@example.com",
    "2026-10-05",
    {"Screw driver set": 2},
    3
)

p4 = Project(
    "P0004",
    "66000004",
    "David",
    "Sensor Project",
    "david@example.com",
    "2026-10-02",
    {"Current sensor (ACS712)": 1},
    4
)

projects = [
    p1,
    p3,
    p4,
    p2
]


print("Projects before Merge Sort:")
for project in projects:
    print(project)


sorted_projects = merge_sort(
    projects
)


print("\nProjects after Merge Sort:")
for project in sorted_projects:
    print(project)


print("\nPriority Order:")
for i in range(len(sorted_projects)):
    print(
        i + 1,
        sorted_projects[i].project_id,
        sorted_projects[i].project_name,
        sorted_projects[i].pickup_date
    )
