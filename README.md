# RAI Student Project Item Allocator (IFP)

> **Priorities always come first.**
>
> KMITL Robotics and AI Engineering (RAI) - Data Structures & Algorithms Mini Project

A web application for RAI students to request and borrow project components and tools. It searches inventory, prioritizes requests using custom algorithms and data structures, and keeps track of reservations, borrowing, returns, and damaged items.

**Admin confirmation is required.** Stock is checked and Pending requests are rechecked automatically, but only an admin can approve a reservation or confirm physical item handover.

See [requirement.md](requirement.md) for the project goals, borrowing/returning workflow, and priority rules.

## Current Features

| Student | Admin |
|---|---|
| Browse, search, and filter inventory | Dashboard with stock and request statistics |
| Submit project information and requested items | Review the priority-ranked Pending queue |
| Receive a Project ID and check request status | Approve & Reserve eligible requests |
| Physically return borrowed items | Confirm item handover |
| | Record good and damaged returns |
| | Send shortage notices and generate daily reports |

Statuses: **Pending -> Reserved -> Borrowed -> Returned**.

Every submitted request enters the Pending queue, even if stock is available. When returned items become available, the system rechecks Pending requests but **does not approve them automatically**.

## Tech Stack

- **Backend:** Python, FastAPI, Uvicorn
- **Frontend:** Jinja2 HTML templates, HTMX, vanilla JavaScript, CSS
- **Database:** SQLite
- **Inventory import:** Excel workbook with openpyxl
- **Notifications:** SMTP email if configured, otherwise console messages
- **Reports:** Word (.docx) export with python-docx

The frontend is **server-rendered by FastAPI**. This version does not need React, Vite, or a separate frontend server.

## Project Structure

~~~text
RAI_inventory/
|-- backend/
|   |-- main.py                 FastAPI pages and HTTP routes
|   |-- allocator.py            Request priorities and borrow/return logic
|   |-- inventory.py            Item search and stock operations
|   |-- models.py               Data models
|   |-- notifications.py        SMTP and console notifications
|   |-- test_email.py           Optional manual email test
|   |-- algor/
|   |   |-- binary_search.py    Binary Search
|   |   +-- merge_sort.py       Merge Sort
|   |-- data_struct/
|   |   |-- hash_table.py       Inventory / project lookups
|   |   |-- min_heap.py         Main and Pending queues
|   |   +-- linked_list.py      Damaged records
|   +-- db/
|       |-- database.py         SQLite persistence
|       |-- app.db              Local application database
|       +-- Database_inven_RAI.xlsx  Initial inventory source
|-- frontend/
|   |-- templates/              Jinja2 pages and HTMX partials
|   +-- static/                 CSS, JS, and logo image
|-- test algor_data/            Manual algorithm/data structure examples
|-- requirement.md              Project goals and workflow
|-- requirements.txt            Python dependencies
|-- pyproject.toml              Python project metadata
+-- README.md                   This file
~~~

**main.py** connects the website to **allocator.py** and **inventory.py**. Those files import real algorithms from **backend/algor/** and data structures from **backend/data_struct/**.

## Run Locally - Windows PowerShell

Use the **RAI_inventory** repository root (not the parent folder):

~~~powershell
cd "RAI_inventory"
~~~

Create a virtual environment if one does not already exist:

~~~powershell
py -m venv .venv
~~~

Install the dependencies:

~~~powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
~~~

Start FastAPI:

~~~powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
~~~

Open **http://127.0.0.1:8000** and choose **Student** or **Admin**. The backend serves the HTML pages and static frontend files; no second frontend command is required.

## Current Workflow

~~~text
Student searches inventory (Binary Search)
  -> Submits project request (Project ID)
  -> Main Min-Heap (earliest pickup date first)
  -> Inventory check (Hash Table)
  -> Pending Min-Heap (every request waits here)
  -> Admin selects highest-priority fulfillable request
  -> Admin clicks Approve & Reserve
  -> Reserved + ready-for-pickup notification
  -> Student collects items; admin confirms handover
  -> Reduce live stock + Borrowed Hash Table
  -> Student returns items; admin checks condition
      |-- Good -> restore usable stock
      +-- Damaged -> Singly Linked List
  -> Mark Returned
  -> Recheck Pending (admin approval still required)
~~~

**Merge Sort** creates ordered admin views and maintains the sorted catalog used by Binary Search. Requests are prioritized by pick-up date, then submission time.

## Storage

- **backend/db/Database_inven_RAI.xlsx** is the source used to seed the inventory when the database has no inventory records.
- **backend/db/app.db** stores inventory, projects, borrowing status, damage records, and activity history.
- The backend restores its working Min-Heaps, Hash Tables, and damage list from SQLite on startup.
- Changes to the Excel workbook **do not automatically overwrite** an existing SQLite inventory.
- Back up the local database before intentionally resetting inventory or project records.

## Email and Reports

Ready-for-pickup notifications are generated when an admin approves a request. Out-of-stock requests can trigger pending notifications, and admins can resend shortage notices.

For real email delivery, set the SMTP configuration in the project-root **.env**: **RAI_SMTP_HOST**, **RAI_SMTP_PORT**, **RAI_SMTP_USERNAME**, **RAI_SMTP_PASSWORD**, **RAI_SMTP_FROM**, and **RAI_SMTP_USE_TLS**. Without SMTP configuration, notices are printed in the terminal.

The admin dashboard includes the **Top 3 borrowed items**. A daily summary shows activity and supports a downloadable **Word (.docx)** report.

## Notes

- Role switching currently uses a cookie and is for demonstration, **not secure authentication**.
- Reservation, stock deduction, and return are separate events: reservation occurs after approval; live stock decreases on handover and increases on good returns.
- Returning items refreshes Pending readiness, but admin approval is always required.
- Manual demonstrations of the required algorithms and data structures are in [test algor_data/](test%20algor_data/).
