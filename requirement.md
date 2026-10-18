# RAI Student Project Item Allocator (IFP)

> **Priorities always come first.**
>
> KMITL Robotics and AI Engineering (RAI) - Data Structures & Algorithms Mini Project

## 1. Project Overview

- **Project:** Item Allocator for Student Projects
- **Group:** ROW
- **Team:** Thiradet Kurdsup (68011571), Sunhanat Panasjaroen (68011526), and Siraphop William Wakeling (68011516)

RAI Item Allocator is a website that helps RAI students request components and tools for university projects. It replaces manual request handling with an inventory catalog, a fair project priority queue, and records of borrowing and returns.

**System responsibility:** Automatically search and check inventory, prioritize requests, and update waiting requests. **Admin responsibility:** Approve reservations, confirm physical collection, and verify returns.

This file describes the **general project idea and current workflow**, not every technical implementation detail. The [README](README.md) explains the code structure and how to run the website.

## 2. Problem and Goals

Manual item allocation takes time, makes priority decisions difficult to track, and can lead to outdated inventory records.

The project aims to:

- Allow students to search the real RAI inventory and submit requests online.
- Prioritize projects fairly by pick-up date and submission time.
- Prevent requests from reserving more stock than is available.
- Require explicit admin approval for reservations and item handover.
- Record items borrowed, returned in good condition, or reported damaged.
- Automatically recheck waiting projects after stock changes.
- Provide useful email/console notifications and activity reports.

## 3. Users and Features

| User | Current features |
|---|---|
| **Student** | Browse and filter inventory; search components/tools; submit project name, student name/ID, email, pick-up date, and requested items; view status using the Project ID; physically return borrowed items. |
| **Admin** | Review priorities and stock; approve and reserve fulfillable requests; confirm handover; classify returned items as good or damaged; view damaged items; resend stock notices; view dashboard statistics and daily reports. |

The current prototype uses a **Student / Admin role selector** rather than secure account-based authentication.

## 4. Borrowing Workflow

1. The student searches inventory. **Binary Search** helps find items in the sorted catalog; available and reserved quantities come from the **Hash Table**.
2. The student submits a request. The system creates a unique **Project ID**.
3. The request enters the **Main Min-Heap** and is processed using priority: earliest pick-up date first, then earliest submission time.
4. The system checks stock for **all requested quantities**, including totals from duplicate lines of the same item.
5. Every new request is placed into the **Pending Min-Heap**. Insufficient stock is recorded as a shortage and triggers a pending notification; requests with available stock still wait for approval.
6. The admin reviews the ranked requests and chooses the **highest-priority request that can be fulfilled**. A higher-priority but out-of-stock request remains Pending.
7. When the admin selects **Approve & Reserve**, the system reserves stock, changes the request to **Reserved**, and sends a ready-for-pickup notification.
8. After the student physically collects the items, the admin selects **Confirm Handover**. Only then does live stock decrease and the request move to the **Borrowed Hash Table**.

**Nothing is automatically approved or reserved simply because items are available.**

## 5. Returning Workflow

1. The student physically returns borrowed components/tools.
2. The admin looks up the borrowed request by **Project ID**.
3. The admin checks quantities and marks each returned item **Good** or **Damaged**.
4. Good items increase available live inventory in the **Hash Table**.
5. Damaged items are recorded in a **Singly Linked List** and are not counted as usable stock.
6. The borrowed record is removed and the project status becomes **Returned**.
7. The system **rechecks Pending requests** for newly available stock. Requests become eligible for admin approval; they are **not automatically approved or reserved**.

## 6. Data Structures and Algorithms

| Structure / algorithm | Why the project uses it |
|---|---|
| **Main Min-Heap** | Process incoming requests in order of priority. |
| **Pending Min-Heap** | Maintain requests awaiting sufficient stock or admin approval. |
| **Hash Table** | Fast item lookup and tracking of reserved, borrowed, and all project records. |
| **Singly Linked List** | Store damaged-item records from returns. |
| **Binary Search** | Exact item and case-insensitive prefix searching in sorted inventory. |
| **Merge Sort** | Display requests ordered by priority and maintain the sorted inventory catalog. |

The website uses these actual implementations from the backend's **algor/** and **data_struct/** folders.

## 7. Business Rules

- Earlier **pick-up date** means higher priority; submission time breaks ties.
- The admin can approve the highest-priority **fulfillable** request.
- **Available quantity = live quantity - reserved quantity.**
- Reservations cannot exceed the available quantity.
- **Approve & Reserve** changes Pending to Reserved without reducing live stock.
- **Confirm Handover** reduces live stock and changes Reserved to Borrowed.
- Good returns restore usable stock; damaged returns go to the damage list.
- Rechecking the Pending queue is automatic after relevant inventory changes; approving requests is always manual.

Status progression: **Pending -> Reserved -> Borrowed -> Returned**.

## 8. Data, Interface, and Reporting

The current prototype uses **FastAPI (Python)**, **Jinja2 HTML templates**, **HTMX**, JavaScript, and CSS. A local **SQLite** database stores state. On an empty inventory database, the initial items come from the RAI **Excel** workbook.

The admin dashboard shows request counts, out-of-stock items, priority rankings, and the **Top 3 borrowed items**. A daily activity report can be downloaded as a **Word (.docx)** document.

When SMTP is configured, notifications are sent by email. Otherwise, they appear in the backend terminal for demonstration.

## 9. Scope and Limitations

**Current prototype:** Inventory browsing and search, request priority, admin-approved reservations, handover, borrowing records, good/damaged returns, Pending rechecks, notifications, and reports.

**Future improvements:** Secure user accounts and admin authentication, stronger concurrent multi-user handling, and production deployment. The current single-process allocator and role-switch cookie are suitable for the course demonstration, not production security.

The core principle is to **automate calculations and tracking while keeping approval and physical borrowing decisions with the admin**.
