"""FastAPI + Jinja2/HTMX web app (section 8 of the brief).

Single-process demo app: one Allocator/Database live in app.state, built
once at startup (rebuilt from SQLite if data already exists, otherwise
seeded from the CSV). Role is a simple cookie set by /login (section 13
default: two hard-coded roles, no real auth).
"""

import os
from contextlib import asynccontextmanager
from datetime import date
from typing import Optional

from fastapi import Cookie, Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from algo.merge_sort import merge_sort
from app.allocator import Allocator
from app.db import Database
from app.inventory import InventoryCatalog
from app.models import (
    ItemCondition,
    ItemStatus,
    RequestLineItem,
    ReturnLineItem,
)
from app.notifications import notifier_from_env

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.environ.get("RAI_DB_PATH", os.path.join(BASE_DIR, "data", "app.db"))
SEED_CSV = os.environ.get("RAI_SEED_CSV", os.path.join(BASE_DIR, "data", "inventory_seed.csv"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = Database(DB_PATH)
    notifier = notifier_from_env()
    if db.load_inventory_items():
        allocator = Allocator.from_db(db, notifier=notifier)
    else:
        catalog = InventoryCatalog()
        catalog.load_csv(SEED_CSV)
        db.save_inventory_items(catalog.all_items())
        allocator = Allocator(catalog, notifier=notifier, db=db)
    app.state.db = db
    app.state.allocator = allocator
    yield
    db.close()


app = FastAPI(title="RAI Student Project Item Allocator", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "app", "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "app", "templates"))


def get_allocator(request: Request) -> Allocator:
    return request.app.state.allocator


def get_role(role: Optional[str] = Cookie(default=None)) -> str:
    return role if role in ("student", "admin") else "student"


def require_admin(role: str = Depends(get_role)) -> str:
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return role


def priority_label(pick_up_date: date, today: date | None = None) -> str:
    today = today or date.today()
    days = (pick_up_date - today).days
    if days <= 1:
        return "High"
    if days <= 3:
        return "Medium"
    return "Low"


def ctx(request: Request, role: str, **extra) -> dict:
    return {"role": role, "active_nav": extra.pop("active_nav", ""), **extra}


# -- auth / role switch --------------------------------------------------


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, role: str = Depends(get_role)):
    return templates.TemplateResponse(request, "login.html", ctx(request, role, active_nav="login"))


@app.post("/login")
def do_login(chosen_role: str = Form(...)):
    if chosen_role not in ("student", "admin"):
        raise HTTPException(status_code=400, detail="invalid role")
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie("role", chosen_role, max_age=60 * 60 * 24 * 30)
    return response


@app.get("/")
def root():
    return RedirectResponse(url="/dashboard")


# -- dashboard -------------------------------------------------------------


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, role: str = Depends(get_role), alloc: Allocator = Depends(get_allocator)):
    items = alloc.catalog.all_items()
    available_types = sum(1 for i in items if i.status == ItemStatus.AVAILABLE)
    reserved_units = sum(i.reserved_qty for i in items)
    shortage_items = merge_sort(
        [i for i in items if i.status in (ItemStatus.LOW_STOCK, ItemStatus.OUT_OF_STOCK)],
        key_func=lambda i: i.available_qty,
    )

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        ctx(
            request,
            role,
            active_nav="dashboard",
            available_types=available_types,
            reserved_units=reserved_units,
            pending_count=len(alloc.pending_heap),
            borrowed_count=len(alloc.borrowed),
            reserved_projects=len(alloc.reserved),
            shortage_items=shortage_items[:15],
            total_items=len(items),
            remaining_stock=sum(i.available_qty for i in items),
        ),
    )


# -- new request -------------------------------------------------------------


@app.get("/new-request", response_class=HTMLResponse)
def new_request_page(request: Request, role: str = Depends(get_role), alloc: Allocator = Depends(get_allocator)):
    return templates.TemplateResponse(
        request,
        "new_request.html",
        ctx(request, role, active_nav="new_request", types=alloc.catalog.types(), today=date.today().isoformat()),
    )


@app.get("/components/search", response_class=HTMLResponse)
def search_components(
    request: Request,
    q: str = "",
    type: str = "",
    role: str = Depends(get_role),
    alloc: Allocator = Depends(get_allocator),
):
    results = alloc.catalog.search_by_name_prefix(q, type_=type or None) if q.strip() else []
    return templates.TemplateResponse(
        request, "_partials/component_results.html", {"results": results[:20]}
    )


@app.post("/requests")
def create_request(
    request: Request,
    project_name: str = Form(...),
    student_name: str = Form(...),
    group: str = Form(...),
    pick_up_date: str = Form(...),
    student_email: str = Form(""),
    item_types: list[str] = Form(default=[]),
    item_names: list[str] = Form(default=[]),
    item_quantities: list[str] = Form(default=[]),
    alloc: Allocator = Depends(get_allocator),
):
    if not item_types:
        raise HTTPException(status_code=400, detail="At least one component/tool is required")
    try:
        pud = date.fromisoformat(pick_up_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid pick-up date")

    lines = []
    for t, n, q in zip(item_types, item_names, item_quantities):
        qty = int(q)
        if qty <= 0:
            raise HTTPException(status_code=400, detail=f"Quantity for {n} must be positive")
        lines.append(RequestLineItem(t, n, qty))

    req = alloc.submit_request(
        project_name=project_name,
        student_name=student_name,
        group=group,
        pick_up_date=pud,
        items=lines,
        student_email=student_email,
    )
    return RedirectResponse(url=f"/requests/{req.project_id}", status_code=303)


@app.get("/requests/{project_id}", response_class=HTMLResponse)
def request_status(
    project_id: str, request: Request, role: str = Depends(get_role), alloc: Allocator = Depends(get_allocator)
):
    req = alloc.all_requests.get(project_id)
    if req is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return templates.TemplateResponse(
        request,
        "request_status.html", ctx(request, role, active_nav="new_request", req=req)
    )


# -- inventory ---------------------------------------------------------------


@app.get("/inventory", response_class=HTMLResponse)
def inventory_page(
    request: Request,
    q: str = "",
    type: str = "",
    role: str = Depends(get_role),
    alloc: Allocator = Depends(get_allocator),
):
    items = alloc.catalog.search_by_name_prefix(q, type_=type or None) if q.strip() else alloc.catalog.all_items()
    if type and not q.strip():
        items = [i for i in items if i.type == type]
    return templates.TemplateResponse(
        request,
        "inventory.html",
        ctx(request, role, active_nav="inventory", items=items, types=alloc.catalog.types(), q=q, selected_type=type),
    )


# -- pending -------------------------------------------------------------


@app.get("/pending", response_class=HTMLResponse)
def pending_page(request: Request, role: str = Depends(get_role), alloc: Allocator = Depends(get_allocator)):
    ordered = merge_sort(alloc.pending_heap.to_list(), key_func=lambda r: r.heap_key)
    return templates.TemplateResponse(
        request,
        "pending.html", ctx(request, role, active_nav="pending", requests=ordered)
    )


# -- borrowed / returns --------------------------------------------------


@app.get("/borrowed", response_class=HTMLResponse)
def borrowed_page(request: Request, role: str = Depends(get_role), alloc: Allocator = Depends(get_allocator)):
    records = merge_sort(list(alloc.borrowed.values()), key_func=lambda r: r.handed_over_at)
    reserved = merge_sort(list(alloc.reserved.values()), key_func=lambda r: r.heap_key)
    return templates.TemplateResponse(
        request,
        "borrowed.html", ctx(request, role, active_nav="borrowed", records=records, reserved=reserved)
    )


@app.post("/reserved/{project_id}/handover")
def do_handover(project_id: str, role: str = Depends(require_admin), alloc: Allocator = Depends(get_allocator)):
    try:
        alloc.confirm_handover(project_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not in Reserved state")
    return RedirectResponse(url="/borrowed", status_code=303)


@app.post("/reserved/{project_id}/release")
def do_release(project_id: str, role: str = Depends(require_admin), alloc: Allocator = Depends(get_allocator)):
    try:
        alloc.release_reservation(project_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not in Reserved state")
    return RedirectResponse(url="/admin", status_code=303)


@app.get("/returns", response_class=HTMLResponse)
def returns_search(
    request: Request,
    project_id: str = "",
    role: str = Depends(get_role),
    alloc: Allocator = Depends(get_allocator),
):
    record = alloc.borrowed.get(project_id) if project_id else None
    error = "Project ID not found in Borrowed" if project_id and record is None else ""
    return templates.TemplateResponse(
        request,
        "returns.html", ctx(request, role, active_nav="returns", project_id=project_id, record=record, error=error)
    )


@app.post("/returns/{project_id}")
def do_return(
    project_id: str,
    request: Request,
    role: str = Depends(require_admin),
    alloc: Allocator = Depends(get_allocator),
    item_types: list[str] = Form(default=[]),
    item_names: list[str] = Form(default=[]),
    good_quantities: list[str] = Form(default=[]),
    damaged_quantities: list[str] = Form(default=[]),
    notes: list[str] = Form(default=[]),
):
    lines: list[ReturnLineItem] = []
    for t, n, good, bad, note in zip(item_types, item_names, good_quantities, damaged_quantities, notes):
        good_q, bad_q = int(good or 0), int(bad or 0)
        if good_q > 0:
            lines.append(ReturnLineItem(t, n, good_q, ItemCondition.GOOD))
        if bad_q > 0:
            lines.append(ReturnLineItem(t, n, bad_q, ItemCondition.DAMAGED, note=note))
    try:
        alloc.process_return(project_id, lines)
    except KeyError:
        raise HTTPException(status_code=404, detail="Project not in Borrowed state")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return RedirectResponse(url="/borrowed", status_code=303)


# -- damaged items -------------------------------------------------------


@app.get("/damaged", response_class=HTMLResponse)
def damaged_page(request: Request, role: str = Depends(get_role), alloc: Allocator = Depends(get_allocator)):
    records = list(alloc.damaged)
    records.reverse()
    return templates.TemplateResponse(
        request,
        "damaged.html", ctx(request, role, active_nav="damaged", records=records)
    )


# -- admin view ------------------------------------------------------------


@app.get("/admin", response_class=HTMLResponse)
def admin_view(request: Request, role: str = Depends(get_role), alloc: Allocator = Depends(get_allocator)):
    rows = alloc.admin_ordered_view()
    today = date.today()
    annotated = [(req, priority_label(req.pick_up_date, today)) for req in rows]
    return templates.TemplateResponse(
        request,
        "admin_view.html", ctx(request, role, active_nav="admin", rows=annotated)
    )
