"""API lokal yang menghubungkan UI dengan modul."""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from dockingku import __version__
from dockingku.config import PROJECTS_DIR
from dockingku.core.jobs import runner
from dockingku.core.pipeline import STEPS, ready_steps
from dockingku.core.project import Project
from dockingku.modules import base

WEB = Path(__file__).parent / "web"
app = FastAPI(title="DockingKu", version=__version__)


class NewProject(BaseModel):
    name: str


@app.get("/api/status")
def status():
    """Modul mana yang siap dan pustaka apa yang belum terpasang."""
    return {"version": __version__, "modules": base.status_all()}


@app.get("/api/steps")
def steps():
    return [s.__dict__ for s in STEPS]


@app.get("/api/projects")
def projects():
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
    return [Project.open(p).name for p in sorted(PROJECTS_DIR.iterdir()) if (p / "project.json").exists()]


@app.post("/api/projects")
def new_project(body: NewProject):
    project = Project.create(PROJECTS_DIR, body.name)
    return {"name": project.name, "root": str(project.root), "ready": ready_steps(project.steps)}


@app.get("/api/rcsb/search")
def rcsb_search(q: str, max_resolution: float = 2.5):
    rcsb = base.load("sources.rcsb")
    return [rcsb.entry(i) for i in rcsb.search(q, max_resolution, limit=10)]


@app.get("/api/pubchem")
def pubchem(name: str):
    return base.load("sources.pubchem").by_name(name).__dict__


@app.get("/api/knapsack")
def knapsack(word: str, field: str = "organism"):
    return base.load("sources.knapsack").search(word, field)


@app.get("/api/druglike")
def druglike(smiles: str):
    try:
        return base.load("admet").druglike(smiles)
    except ValueError as exc:
        raise HTTPException(400, str(exc))


@app.get("/api/jobs/{job_id}")
def job(job_id: str):
    j = runner.jobs.get(job_id)
    if not j:
        raise HTTPException(404, "pekerjaan tidak ditemukan")
    return {"id": j.id, "title": j.title, "status": j.status, "progress": j.progress, "message": j.message}


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")


app.mount("/web", StaticFiles(directory=WEB), name="web")
