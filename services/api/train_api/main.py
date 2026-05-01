from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from train_core.agents import (
    build_agent_launch_plan,
    get_agent_status,
    list_agent_adapters,
    serialize_agent_status,
    serialize_launch_plan,
)
from train_core.config import settings
from train_core.db import get_db, init_db
from train_core.models import ProjectState, RunRecord
from train_core.operator import (
    OperatorError,
    build_operator_snapshot,
    resume_run_record,
    touch_run_heartbeat,
)
from train_core.projects import (
    ProjectBootstrapResult,
    ProjectMutation,
    ProjectMutationError,
    bootstrap_project_workspace,
    create_managed_project,
    delete_managed_project,
    get_project,
    list_projects,
    list_reference_projects,
    update_managed_project,
)
from train_core.providers import (
    get_provider_status,
    list_provider_adapters,
    serialize_provider_status,
)
from train_core.ratchet import RatchetError, apply_ratchet_decision
from train_core.runner import (
    RunnerError,
    complete_run_record,
    create_run_record,
    execute_run_record,
    start_run_record,
)
from train_core.schemas import (
    AgentAdapterRead,
    AgentLaunchPlanRead,
    AgentStatusRead,
    OperatorStatusRead,
    ProviderAdapterRead,
    ProviderStatusRead,
    ProjectBootstrapRead,
    ProjectBootstrapRequest,
    ProjectRead,
    ProjectWrite,
    ProjectStateRead,
    RunComplete,
    RunCreate,
    RunHeartbeat,
    RunRead,
)

@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield

app = FastAPI(title=settings.app_name, lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.train_env,
    }


@app.get("/v1/projects", response_model=list[ProjectRead])
def get_projects(db: Session = Depends(get_db)) -> list[ProjectRead]:
    return [ProjectRead.model_validate(project, from_attributes=True) for project in list_projects(db)]


@app.get("/v1/projects/templates", response_model=list[ProjectRead])
def get_project_templates() -> list[ProjectRead]:
    return [ProjectRead.model_validate(project, from_attributes=True) for project in list_reference_projects()]


@app.get("/v1/projects/{project_key}", response_model=ProjectRead)
def get_project_by_key(project_key: str, db: Session = Depends(get_db)) -> ProjectRead:
    project = get_project(project_key, db=db)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectRead.model_validate(project, from_attributes=True)


@app.post("/v1/projects", response_model=ProjectRead, status_code=201)
def create_project(payload: ProjectWrite, db: Session = Depends(get_db)) -> ProjectRead:
    try:
        project = create_managed_project(db, _project_mutation_from_payload(payload))
    except ProjectMutationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ProjectRead.model_validate(project, from_attributes=True)


@app.put("/v1/projects/{project_key}", response_model=ProjectRead)
def update_project(project_key: str, payload: ProjectWrite, db: Session = Depends(get_db)) -> ProjectRead:
    try:
        project = update_managed_project(db, project_key, _project_mutation_from_payload(payload))
    except ProjectMutationError as exc:
        status_code = 404 if "was not found" in str(exc) else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return ProjectRead.model_validate(project, from_attributes=True)


@app.delete("/v1/projects/{project_key}", status_code=204)
def delete_project(project_key: str, db: Session = Depends(get_db)) -> None:
    try:
        delete_managed_project(db, project_key)
    except ProjectMutationError as exc:
        status_code = 404 if "was not found" in str(exc) else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc


@app.post("/v1/projects/{project_key}/bootstrap", response_model=ProjectBootstrapRead)
def bootstrap_project(
    project_key: str,
    payload: ProjectBootstrapRequest,
    db: Session = Depends(get_db),
) -> ProjectBootstrapRead:
    project = get_project(project_key, db=db)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.source_kind != "managed":
        raise HTTPException(status_code=400, detail="Only managed projects can be bootstrapped.")
    try:
        result = bootstrap_project_workspace(project, overwrite=payload.overwrite)
    except ProjectMutationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _serialize_project_bootstrap(result)


@app.get("/v1/agents", response_model=list[AgentAdapterRead])
def get_agent_adapters() -> list[AgentAdapterRead]:
    return [AgentAdapterRead.model_validate(adapter, from_attributes=True) for adapter in list_agent_adapters()]


@app.get("/v1/agents/{agent_key}", response_model=AgentStatusRead)
def get_agent_adapter_status(agent_key: str) -> AgentStatusRead:
    try:
        status = get_agent_status(agent_key)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return AgentStatusRead.model_validate(serialize_agent_status(status))


@app.get("/v1/agents/{agent_key}/launch-plan", response_model=AgentLaunchPlanRead)
def get_agent_launch_plan(
    agent_key: str,
    project_key: str,
    mode: str = "plan",
    objective: str | None = None,
    max_turns: int | None = None,
) -> AgentLaunchPlanRead:
    try:
        plan = build_agent_launch_plan(
            adapter_key=agent_key,
            project_key=project_key,
            mode=mode,
            objective=objective,
            max_turns=max_turns,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AgentLaunchPlanRead.model_validate(serialize_launch_plan(plan))


@app.get("/v1/providers", response_model=list[ProviderAdapterRead])
def get_provider_adapters() -> list[ProviderAdapterRead]:
    return [
        ProviderAdapterRead.model_validate(provider, from_attributes=True)
        for provider in list_provider_adapters()
    ]


@app.get("/v1/providers/{provider_key}", response_model=ProviderStatusRead)
def get_provider_adapter_status(provider_key: str) -> ProviderStatusRead:
    try:
        status = get_provider_status(provider_key)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ProviderStatusRead.model_validate(serialize_provider_status(status))


@app.get("/v1/operator/status", response_model=OperatorStatusRead)
def get_operator_status(db: Session = Depends(get_db)) -> OperatorStatusRead:
    snapshot = build_operator_snapshot(db)
    return OperatorStatusRead.model_validate(snapshot, from_attributes=True)


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


@app.post("/v1/runs/{run_id}/heartbeat", response_model=RunRead)
def heartbeat_run(
    run_id: int,
    payload: RunHeartbeat,
    db: Session = Depends(get_db),
) -> RunRecord:
    run = db.get(RunRecord, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    try:
        return touch_run_heartbeat(db, run, payload.lease_seconds)
    except OperatorError as exc:
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


@app.post("/v1/runs/{run_id}/resume", response_model=RunRead)
def resume_run(run_id: int, db: Session = Depends(get_db)) -> RunRecord:
    run = db.get(RunRecord, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    try:
        return resume_run_record(db, run)
    except OperatorError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/v1/runs/{run_id}", response_model=RunRead)
def get_run(run_id: int, db: Session = Depends(get_db)) -> RunRecord:
    run = db.get(RunRecord, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


def _project_mutation_from_payload(payload: ProjectWrite) -> ProjectMutation:
    return ProjectMutation(
        key=payload.key,
        name=payload.name,
        description=payload.description,
        mutable_artifact=payload.mutable_artifact,
        autonomous_mutable_artifacts=payload.autonomous_mutable_artifacts,
        setup_artifacts=payload.setup_artifacts,
        dependency_artifacts=payload.dependency_artifacts,
        metric_name=payload.metric_name,
        metric_direction=payload.metric_direction,
        min_budget_seconds=payload.min_budget_seconds,
        default_budget_seconds=payload.default_budget_seconds,
        max_budget_seconds=payload.max_budget_seconds,
        runner_key=payload.runner_key,
        execution_entrypoint=payload.execution_entrypoint,
        template_key=payload.template_key,
    )


def _serialize_project_bootstrap(result: ProjectBootstrapResult) -> ProjectBootstrapRead:
    return ProjectBootstrapRead(
        project_key=result.project_key,
        project_root=result.project_root,
        created_files=result.created_files,
        overwritten_files=result.overwritten_files,
        skipped_files=result.skipped_files,
    )
