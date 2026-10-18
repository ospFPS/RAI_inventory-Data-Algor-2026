from pathlib import Path
import base64
import hashlib
import io
import json
import textwrap
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "RAI_Inventory_Colab_Demo.ipynb"

files = list((ROOT / "backend").rglob("*.py"))
files += list((ROOT / "frontend" / "templates").rglob("*.html"))
files += [p for p in (ROOT / "frontend" / "static").rglob("*") if p.is_file() and p.suffix.lower() in {".js", ".css", ".png", ".svg", ".ico", ".webp", ".jpg", ".jpeg"}]
files += [ROOT / "backend/db/Database_inven_RAI.xlsx", ROOT / "requirements.txt"]
files += [ROOT / name for name in ("README.md", "requirement.md") if (ROOT / name).is_file()]
files = sorted(set(files), key=lambda p: p.relative_to(ROOT).as_posix())
assert all(p.is_file() for p in files)
assert not any(p.suffix.lower() in (".db", ".pyc", ".env") for p in files)
assert (ROOT / "frontend/static/request.js") in files

raw_zip = io.BytesIO()
manifest = {}
with zipfile.ZipFile(raw_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for path in files:
        name = path.relative_to(ROOT).as_posix()
        payload = path.read_bytes()
        manifest[name] = hashlib.sha256(payload).hexdigest()
        z.writestr(name, payload)
    z.writestr("_snapshot_manifest.json", json.dumps(manifest, indent=2))
archive = raw_zip.getvalue()
encoded = base64.b64encode(archive).decode()
checksum = hashlib.sha256(archive).hexdigest()

def md(source):
    return {"cell_type": "markdown", "metadata": {},
            "source": textwrap.dedent(source).strip().splitlines(keepends=True)}

def py(source, hidden=False):
    source = textwrap.dedent(source).strip() + "\n"
    compile(source, "notebook", "exec")
    metadata = {"colab": {"cellView": "form"}} if hidden else {}
    return {"cell_type": "code", "execution_count": None, "metadata": metadata,
            "outputs": [], "source": source.splitlines(keepends=True)}

cells = [
    md("""
    # RAI Inventory - Full Website Demo (Google Colab)

    This notebook contains an embedded snapshot of the **real, working RAI Inventory project**:
    backend Python, Min-Heap, Hash Table, Binary Search, Merge Sort, Linked List,
    FastAPI web routes, HTML templates, JavaScript, CSS, logo, and the **original RAI Excel workbook**.

    **For the professor:** Open in Google Colab, choose **Runtime > Run all**, and scroll to
    **Step 6** to open the temporary website. Choose **Student** or **Admin** and test the workflows.
    Use the Colab **Files** panel to browse the extracted original Python and HTML source files.

    **Safety and privacy:** The actual Windows application database, database backups,
    environment file, and SMTP credentials are **not included**. This notebook creates a
    new SQLite database in temporary Colab storage and seeds it from the bundled Excel workbook.
    Demo edits cannot change the original application database. The real Excel inventory
    is included, so distribute the notebook only to authorized recipients.

    The role selector is a course demo rather than secure account authentication.
    The temporary website link works only while the professor's Colab runtime is active.
    When the project source changes, regenerate this notebook to include newer code.
    """),
    py(
        "# @title Step 1 - Embedded real project source and Excel file (run, no editing needed)\n"
        + "SOURCE_ARCHIVE_SHA256 = " + repr(checksum) + "\n"
        + "FILE_COUNT = " + str(len(files)) + "\n"
        + "SOURCE_ARCHIVE = (\n"
        + "".join("    " + repr(encoded[i:i+120]) + "\n" for i in range(0, len(encoded), 120))
        + ")\n", hidden=True),
    py("""
    # @title Step 2 - Unpack all real project files (no existing database)
    import base64, hashlib, io, json, tempfile, zipfile
    from pathlib import Path, PurePosixPath

    packed = base64.b64decode(SOURCE_ARCHIVE)
    assert hashlib.sha256(packed).hexdigest() == SOURCE_ARCHIVE_SHA256
    DEMO_HOME = Path(tempfile.mkdtemp(prefix="rai_prof_demo_", dir="/content" if Path("/content").is_dir() else None))
    PROJECT = DEMO_HOME / "RAI_inventory"
    PROJECT.mkdir()
    with zipfile.ZipFile(io.BytesIO(packed)) as z:
        for entry in z.infolist():
            relative = PurePosixPath(entry.filename)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("Unsafe bundled filename")
            target = PROJECT.joinpath(*relative.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            if not entry.is_dir():
                target.write_bytes(z.read(entry.filename))
    manifest = json.loads((PROJECT / "_snapshot_manifest.json").read_text())
    assert len(manifest) == FILE_COUNT
    for relative, digest in manifest.items():
        assert hashlib.sha256((PROJECT / relative).read_bytes()).hexdigest() == digest
    EXCEL = PROJECT / "backend/db/Database_inven_RAI.xlsx"
    assert EXCEL.is_file()
    assert not list(PROJECT.rglob("*.db"))
    assert not (PROJECT / ".env").exists()
    print("Verified", FILE_COUNT, "genuine project files including Excel.")
    print("Source location:", PROJECT)
    print("Original app.db and .env: NOT included.")
    """),
    py("""
    # @title Step 3 - Install dependencies from the real project
    import subprocess, sys
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "-r", str(PROJECT / "requirements.txt")],
        check=True,
    )
    print("All requirements installed.")
    """),
    py("""
    # @title Step 4 - Smoke test REAL algorithms with the REAL Excel inventory
    import sys
    from datetime import date

    sys.path.insert(0, str(PROJECT))
    from backend.allocator import Allocator
    from backend.inventory import InventoryCatalog
    from backend.models import RequestLineItem, ReturnLineItem, ItemCondition, RequestStatus

    catalog = InventoryCatalog()
    count = catalog.load_xlsx(EXCEL)
    real_item = next(item for item in catalog.all_items() if item.available_qty > 0)
    assert catalog.get(real_item.type, real_item.item_name) is real_item
    assert any(x.key == real_item.key for x in catalog.search_by_name_prefix(real_item.item_name[:3], real_item.type))

    # This uses real application classes and does NOT write to SQLite.
    trial_catalog = InventoryCatalog()
    trial_catalog.bulk_load([type(real_item)(real_item.type, real_item.item_name, real_item.live_qty)])
    engine = Allocator(trial_catalog)
    request = engine.submit_request(
        project_name="Professor Test",
        student_name="Professor",
        group="Demo",
        pick_up_date=date.today(),
        items=[RequestLineItem(real_item.type, real_item.item_name, 1)],
    )
    assert request.status == RequestStatus.PENDING
    engine.approve_pending_request(request.project_id)
    assert request.status == RequestStatus.RESERVED
    engine.confirm_handover(request.project_id)
    assert request.status == RequestStatus.BORROWED
    engine.process_return(request.project_id, [
        ReturnLineItem(real_item.type, real_item.item_name, 1, ItemCondition.GOOD)
    ])
    assert request.status == RequestStatus.RETURNED
    assert trial_catalog.get(real_item.type, real_item.item_name).live_qty == real_item.live_qty
    print("PASS: Loaded", count, "authentic inventory items from Excel")
    print("PASS: Binary Search and Hash Table lookup")
    print("PASS: Submit > Pending > Admin approval > Borrowed > Returned")
    print("PASS: Live database not accessed")
    """),
    py("""
    # @title Step 5 - Launch full FastAPI website using a NEW SQLite file
    import os, socket, subprocess, sys, time, urllib.error, urllib.request
    from pathlib import Path

    if "web_process" in globals() and web_process.poll() is None:
        web_process.terminate()
        try:
            web_process.wait(timeout=7)
        except subprocess.TimeoutExpired:
            web_process.kill()
            web_process.wait()

    SESSION = Path(tempfile.mkdtemp(prefix="website_", dir=DEMO_HOME))
    DEMO_DATABASE = SESSION / "demo.sqlite3"
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        PORT = s.getsockname()[1]

    env = os.environ.copy()
    env["RAI_DB_PATH"] = str(DEMO_DATABASE)
    env["RAI_XLSX"] = str(EXCEL)
    env["RAI_SMTP_HOST"] = ""
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    SERVER_LOG = SESSION / "server.log"
    log_stream = SERVER_LOG.open("w", encoding="utf-8")
    web_process = subprocess.Popen(
        [sys.executable, "-u", "-m", "uvicorn", "backend.main:app",
         "--host", "0.0.0.0", "--port", str(PORT)],
        cwd=PROJECT,
        env=env,
        stdout=log_stream,
        stderr=subprocess.STDOUT,
    )
    for _ in range(60):
        if web_process.poll() is not None:
            raise RuntimeError("Web server exited: " + SERVER_LOG.read_text()[-2500:])
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/login", timeout=2) as r:
                if r.status == 200:
                    break
        except (urllib.error.URLError, TimeoutError):
            time.sleep(1)
    else:
        raise RuntimeError("FastAPI timeout: " + SERVER_LOG.read_text()[-2500:])

    import sqlite3
    with sqlite3.connect(DEMO_DATABASE) as db:
        inventory_count = db.execute("SELECT COUNT(*) FROM inventory_items").fetchone()[0]
        request_count = db.execute("SELECT COUNT(*) FROM requests").fetchone()[0]
    assert inventory_count > 0 and request_count == 0
    print("Website READY on port", PORT)
    print("Isolated SQLite demo database:", DEMO_DATABASE)
    print("Real inventory items:", inventory_count, "| Student requests:", request_count)
    """),
    py("""
    # @title Step 6 - OPEN YOUR TEMPORARY WEBSITE
    from google.colab import output
    from IPython.display import HTML, display
    from html import escape

    try:
        proxy = output.eval_js(f"google.colab.kernel.proxyPort({PORT})")
        website_url = proxy.rstrip("/") + "/login"
        display(HTML(
            "<p style='font-size:20px'><a href='" + escape(website_url, quote=True)
            + "' target='_blank' rel='noopener noreferrer'>"
            + "OPEN RAI INVENTORY WEBSITE (TEMPORARY)</a></p>"
        ))
        print("Browser link:", website_url)
    except Exception as exc:
        print("New-tab link unavailable:", exc)
        print("Please use the embedded site below instead.")

    output.serve_kernel_port_as_iframe(PORT, path="/login", width="100%", height="700")
    print("The site stays available only while this Colab runtime is running.")
    """),
    md("""
    ## Test the website

    1. Open the generated site and choose **Student**.
    2. Search the **Inventory**, create a **New Request**, and save the Project ID.
    3. Choose **Switch role > Admin**. Open **Pending**, then **Approve & Reserve**.
    4. Open **Borrowed** and confirm handover.
    5. Under **Returns**, enter the Project ID and record good and/or damaged items.
    6. Explore **Damaged**, **Dashboard**, and the daily **Word report**.

    All new requests start Pending; stock becomes reserved only after admin approval.
    Returning usable items refreshes pending requests but does NOT approve them automatically.

    To reset the demo, rerun **Step 5**, creating a new empty SQLite database seeded
    from the Excel workbook. To finish, use **Runtime > Disconnect and delete runtime**.
    """),
]

notebook = {
    "cells": cells,
    "metadata": {
        "colab": {"name": TARGET.name, "provenance": []},
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

for idx, cell in enumerate(cells):
    cell["id"] = hashlib.sha256(str(idx).encode()).hexdigest()[:12]

TARGET.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("Notebook:", TARGET)
print("Bundled files:", len(files))
print("Embedded Excel checksum:", manifest["backend/db/Database_inven_RAI.xlsx"])
print("Notebook bytes:", TARGET.stat().st_size)

