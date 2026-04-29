from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from autotrain_core.config import settings
from autotrain_core.db import get_db, init_db
from autotrain_core.models import ProjectState, RunRecord
from autotrain_core.projects import list_projects
from autotrain_core.ratchet import RatchetError, apply_ratchet_decision
from autotrain_core.runner import (
    RunnerError,
    complete_run_record,
    create_run_record,
    execute_run_record,
    start_run_record,
)
from autotrain_core.schemas import ProjectRead, ProjectStateRead, RunComplete, RunCreate, RunRead


app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.autotrain_env,
    }


@app.get("/v1/projects", response_model=list[ProjectRead])
def get_projects() -> list[ProjectRead]:
    return [ProjectRead.model_validate(project, from_attributes=True) for project in list_projects()]


@app.get("/v1/runs", response_model=list[RunRead])
def list_runs(db: Session = Depends(get_db)) -> list[RunRecord]:
    query = select(RunRecord).order_by(RunRecord.created_at.desc())
    return list(db.scalars(query))


@app.get("/v1/project-states", response_model=list[ProjectStateRead])
def list_project_states(db: Session = Depends(get_db)) -> list[ProjectState]:
    query = select(ProjectState).order_by(ProjectState.project_key.asc())
    return list(db.scalars(query))


@app.post("/v1/runs", response_model=RunRead)
def create_run(payload: RunCreate, db: Session = Depends(get_db)) -> RunRecord:
    try:
        return create_run_record(db, payload)
    except RunnerError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/v1/runs/{run_id}/start", response_model=RunRead)
def start_run(run_id: int, db: Session = Depends(get_db)) -> RunRecord:
    run = db.get(RunRecord, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    try:
        return start_run_record(db, run)
    except RunnerError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/v1/runs/{run_id}/complete", response_model=RunRead)
def complete_run(run_id: int, payload: RunComplete, db: Session = Depends(get_db)) -> RunRecord:
    run = db.get(RunRecord, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    try:
        return complete_run_record(db, run, payload)
    except RunnerError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/v1/runs/{run_id}/execute", response_model=RunRead)
def execute_run(run_id: int, db: Session = Depends(get_db)) -> RunRecord:
    run = db.get(RunRecord, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    try:
        return execute_run_record(db, run)
    except RunnerError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/v1/runs/{run_id}/ratchet", response_model=RunRead)
def ratchet_run(run_id: int, db: Session = Depends(get_db)) -> RunRecord:
    run = db.get(RunRecord, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    try:
        return apply_ratchet_decision(db, run)
    except RatchetError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/v1/runs/{run_id}", response_model=RunRead)
def get_run(run_id: int, db: Session = Depends(get_db)) -> RunRecord:
    run = db.get(RunRecord, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
