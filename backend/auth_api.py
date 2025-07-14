from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from supabase import create_client, Client
import subprocess, os, markdown, re
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()  # ✅ Only once!
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup")
async def signup(username: str = Form(...), password: str = Form(...), email: str = Form(...)):
    supabase.table("userdb").insert({"username": username, "password": password, "email": email}).execute()
    return RedirectResponse(url="/login", status_code=303)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    resp = supabase.table("userdb").select("*").eq("username", username).eq("password", password).execute()
    return RedirectResponse(url="/loading", status_code=303) if resp.data else HTMLResponse("Login failed. <a href='/login'>Try again</a>")


@app.get("/loading", response_class=HTMLResponse)
async def loading(request: Request):
    return templates.TemplateResponse("loading.html", {"request": request})


@app.post("/start-processing")
async def start_processing():
    try:
        base = os.path.dirname(__file__)
        subprocess.run(["python", os.path.join(base, "lstm_project", "auto_update_autodb.py")], check=True)
        subprocess.run(["python", os.path.join(base, "lstm_project", "retrain_lstm_if_needed.py")], check=True)
        subprocess.run(["python", os.path.join(base, "abc_engine","expiry_and_action.py")], check=True)
        subprocess.run(["python", os.path.join(base, "abc_engine", "create_store_reports.py")], check=True)
    except subprocess.CalledProcessError:
        return {"detail": "Failed to generate reports"}
    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    stores = supabase.table("stores").select("store_id, geo, religion").execute().data
    return templates.TemplateResponse("dashboard.html", {"request": request, "stores": stores})


@app.get("/store_report/{store_id}", response_class=HTMLResponse)
async def store_report(request: Request, store_id: str):
    report_path = os.path.join(os.path.dirname(__file__), f"store_{store_id}_report.md")
    if not os.path.exists(report_path):
        return HTMLResponse(f"Report for {store_id} not found.", status_code=404)

    with open(report_path, encoding="utf-8") as f:
        content = f.read()

    # Split at "Detailed Report" heading
    match = re.search(r"^Detailed Report\s*$", content, re.MULTILINE | re.IGNORECASE)
    if match:
        idx = match.start()
        table_md = content[:idx].strip()
        expl_md = content[idx:].strip()
    else:
        table_md = content
        expl_md = ""

    table_html = markdown.markdown(table_md, extensions=["tables"])
    explanation_html = markdown.markdown(expl_md)

    return templates.TemplateResponse("store_report.html", {
        "request": request,
        "store_id": store_id,
        "table_html": table_html,
        "explanation_html": explanation_html
    })
