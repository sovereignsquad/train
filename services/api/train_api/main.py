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
from train_core.datasets import (
    EvalDatasetError,
    create_eval_dataset,
    create_eval_dataset_slice,
    delete_eval_dataset,
    delete_eval_dataset_slice,
    get_eval_dataset,
    get_eval_dataset_slice,
    list_eval_dataset_slices,
    list_eval_datasets,
    serialize_eval_dataset,
    serialize_eval_dataset_slice,
)
from train_core.db import get_db, init_db
from train_core.fine_tuning import (
    FineTuningContractError,
    create_adapter_artifact,
    create_training_spec,
    delete_adapter_artifact,
    delete_training_spec,
    get_adapter_artifact,
    get_training_spec,
    list_adapter_artifacts,
    list_training_specs,
    serialize_adapter_artifact,
    serialize_training_spec,
)
from train_core.grader_suites import (
    GraderSuiteError,
    create_grader_suite,
    delete_grader_suite,
    get_grader_suite,
    list_grader_suites,
    run_grader_suite,
    serialize_grader_suite,
)
from train_core.health import build_doctor_report, check_training_lane_readiness
from train_core.mlx_lm_worker import MlxLmWorkerError, run_training_spec_with_mlx_lm
from train_core.models import ProjectState, RunRecord
from train_core.ollama_packaging import OllamaPackagingError, package_adapter_artifact_for_ollama
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
    AdapterArtifactRead,
    AdapterArtifactWrite,
    AgentAdapterRead,
    AgentLaunchPlanRead,
    AgentStatusRead,
    EvalDatasetRead,
    EvalDatasetSliceRead,
    EvalDatasetSliceWrite,
    EvalDatasetWrite,
    GraderSuiteRead,
    GraderSuiteRunRead,
    GraderSuiteRunRequest,
    GraderSuiteWrite,
    HealthReportRead,
    OllamaPackageRead,
    OllamaPackageRequest,
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
    TrinityReplyPolicyProposalRead,
    TrinityReplyPolicyProposalRequest,
    TrinitySkepticalEvalRead,
    TrinitySkepticalEvalRequest,
    TrinitySpotPolicyProposalRead,
    TrinitySpotPolicyProposalRequest,
    SelfLearningCycleRead,
    SelfLearningCycleRequest,
    TrainingReadinessRead,
    TrainingSpecRead,
    TrainingSpecRunRead,
    TrainingSpecRunRequest,
    TrainingSpecWrite,
)
from train_core.self_learning_cycle import SelfLearningCycleError, run_daily_self_learning_cycle
from train_core.trinity_reply_policy_service import propose_reply_policy_from_bundle_files
from train_core.trinity_skeptical_eval import build_skeptical_eval_report
from train_core.trinity_spot_policy_service import propose_spot_review_policy_from_bundle_files

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


@app.get("/v1/doctor", response_model=HealthReportRead)
def get_doctor_report(
    workflow: str = "default",
    api_base_url: str | None = None,
    trinity_root: str | None = None,
) -> HealthReportRead:
    if workflow not in {"default", "training"}:
        raise HTTPException(status_code=400, detail="workflow must be 'default' or 'training'")
    report = build_doctor_report(
        workflow=workflow,
        api_base_url=api_base_url,
        trinity_root=trinity_root,
    )
    return HealthReportRead.model_validate(report.to_payload())


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


@app.get("/v1/eval-datasets", response_model=list[EvalDatasetRead])
def get_eval_datasets(db: Session = Depends(get_db)) -> list[EvalDatasetRead]:
    return [serialize_eval_dataset(dataset) for dataset in list_eval_datasets(db)]


@app.get("/v1/training-specs", response_model=list[TrainingSpecRead])
def get_training_specs_route(db: Session = Depends(get_db)) -> list[TrainingSpecRead]:
    return [serialize_training_spec(item) for item in list_training_specs(db)]


@app.post("/v1/training-specs", response_model=TrainingSpecRead, status_code=201)
def create_training_spec_route(
    payload: TrainingSpecWrite,
    db: Session = Depends(get_db),
) -> TrainingSpecRead:
    try:
        return serialize_training_spec(create_training_spec(db, payload))
    except (EvalDatasetError, FineTuningContractError, GraderSuiteError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/v1/training-specs/{spec_key}/versions/{spec_version}", response_model=TrainingSpecRead)
def get_training_spec_by_version(
    spec_key: str,
    spec_version: str,
    db: Session = Depends(get_db),
) -> TrainingSpecRead:
    item = get_training_spec(spec_key, spec_version, db)
    if item is None:
        raise HTTPException(status_code=404, detail="Training spec not found")
    return serialize_training_spec(item)


@app.get(
    "/v1/training-specs/{spec_key}/versions/{spec_version}/readiness",
    response_model=TrainingReadinessRead,
)
def get_training_spec_readiness(
    spec_key: str,
    spec_version: str,
    db: Session = Depends(get_db),
) -> TrainingReadinessRead:
    spec = get_training_spec(spec_key, spec_version, db)
    if spec is None:
        raise HTTPException(status_code=404, detail="Training spec not found")
    check = check_training_lane_readiness(required=True, spec=spec)
    return TrainingReadinessRead.model_validate(
        {
            "training_spec_ref": spec.ref,
            "status": check.status,
            "summary": check.summary,
            "details": check.details,
            "remediation": check.remediation,
        }
    )


@app.delete("/v1/training-specs/{spec_key}/versions/{spec_version}", status_code=204)
def delete_training_spec_by_version(
    spec_key: str,
    spec_version: str,
    db: Session = Depends(get_db),
) -> None:
    try:
        delete_training_spec(db, spec_key, spec_version)
    except FineTuningContractError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post(
    "/v1/training-specs/{spec_key}/versions/{spec_version}/runs",
    response_model=TrainingSpecRunRead,
    status_code=201,
)
def run_training_spec_route(
    spec_key: str,
    spec_version: str,
    payload: TrainingSpecRunRequest,
    db: Session = Depends(get_db),
) -> TrainingSpecRunRead:
    try:
        return run_training_spec_with_mlx_lm(spec_key, spec_version, payload, db)
    except (FineTuningContractError, MlxLmWorkerError) as exc:
        status_code = 404 if "was not found" in str(exc) else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc


@app.get("/v1/adapter-artifacts", response_model=list[AdapterArtifactRead])
def get_adapter_artifacts_route(db: Session = Depends(get_db)) -> list[AdapterArtifactRead]:
    return [serialize_adapter_artifact(item) for item in list_adapter_artifacts(db)]


@app.post("/v1/adapter-artifacts", response_model=AdapterArtifactRead, status_code=201)
def create_adapter_artifact_route(
    payload: AdapterArtifactWrite,
    db: Session = Depends(get_db),
) -> AdapterArtifactRead:
    try:
        return serialize_adapter_artifact(create_adapter_artifact(db, payload))
    except FineTuningContractError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/v1/adapter-artifacts/{artifact_key}/versions/{artifact_version}", response_model=AdapterArtifactRead)
def get_adapter_artifact_by_version(
    artifact_key: str,
    artifact_version: str,
    db: Session = Depends(get_db),
) -> AdapterArtifactRead:
    item = get_adapter_artifact(artifact_key, artifact_version, db)
    if item is None:
        raise HTTPException(status_code=404, detail="Adapter artifact not found")
    return serialize_adapter_artifact(item)


@app.post(
    "/v1/adapter-artifacts/{artifact_key}/versions/{artifact_version}/ollama-package",
    response_model=OllamaPackageRead,
    status_code=201,
)
def package_adapter_artifact_for_ollama_route(
    artifact_key: str,
    artifact_version: str,
    payload: OllamaPackageRequest,
    db: Session = Depends(get_db),
) -> OllamaPackageRead:
    try:
        result = package_adapter_artifact_for_ollama(
            artifact_key=artifact_key,
            artifact_version=artifact_version,
            ollama_model_name=payload.ollama_model_name,
            output_dir=payload.output_dir,
            temperature=payload.temperature,
            top_p=payload.top_p,
            system_prompt=payload.system_prompt,
            db=db,
        )
    except (FineTuningContractError, OllamaPackagingError) as exc:
        status_code = 404 if "was not found" in str(exc) else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return OllamaPackageRead.model_validate(
        {
            "ollama_model_name": result.ollama_model_name,
            "modelfile_path": result.modelfile_path,
            "metadata_path": result.metadata_path,
            "output_dir": result.output_dir,
            "created_at": result.created_at,
            "adapter_artifact": result.adapter_artifact.model_dump(mode="json"),
        }
    )


@app.delete("/v1/adapter-artifacts/{artifact_key}/versions/{artifact_version}", status_code=204)
def delete_adapter_artifact_by_version(
    artifact_key: str,
    artifact_version: str,
    db: Session = Depends(get_db),
) -> None:
    try:
        delete_adapter_artifact(db, artifact_key, artifact_version)
    except FineTuningContractError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/v1/eval-datasets", response_model=EvalDatasetRead, status_code=201)
def create_eval_dataset_route(
    payload: EvalDatasetWrite,
    db: Session = Depends(get_db),
) -> EvalDatasetRead:
    try:
        return serialize_eval_dataset(create_eval_dataset(db, payload))
    except EvalDatasetError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/v1/eval-datasets/{dataset_key}/versions/{dataset_version}", response_model=EvalDatasetRead)
def get_eval_dataset_by_version(
    dataset_key: str,
    dataset_version: str,
    db: Session = Depends(get_db),
) -> EvalDatasetRead:
    dataset = get_eval_dataset(dataset_key, dataset_version, db)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Eval dataset not found")
    return serialize_eval_dataset(dataset)


@app.delete("/v1/eval-datasets/{dataset_key}/versions/{dataset_version}", status_code=204)
def delete_eval_dataset_by_version(
    dataset_key: str,
    dataset_version: str,
    db: Session = Depends(get_db),
) -> None:
    try:
        delete_eval_dataset(db, dataset_key, dataset_version)
    except EvalDatasetError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get(
    "/v1/eval-datasets/{dataset_key}/versions/{dataset_version}/slices",
    response_model=list[EvalDatasetSliceRead],
)
def get_eval_dataset_slices_route(
    dataset_key: str,
    dataset_version: str,
    db: Session = Depends(get_db),
) -> list[EvalDatasetSliceRead]:
    return [
        serialize_eval_dataset_slice(item)
        for item in list_eval_dataset_slices(dataset_key, dataset_version, db)
    ]


@app.post(
    "/v1/eval-datasets/{dataset_key}/versions/{dataset_version}/slices",
    response_model=EvalDatasetSliceRead,
    status_code=201,
)
def create_eval_dataset_slice_route(
    dataset_key: str,
    dataset_version: str,
    payload: EvalDatasetSliceWrite,
    db: Session = Depends(get_db),
) -> EvalDatasetSliceRead:
    try:
        return serialize_eval_dataset_slice(
            create_eval_dataset_slice(db, dataset_key, dataset_version, payload)
        )
    except EvalDatasetError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get(
    "/v1/eval-datasets/{dataset_key}/versions/{dataset_version}/slices/{slice_key}/versions/{slice_version}",
    response_model=EvalDatasetSliceRead,
)
def get_eval_dataset_slice_by_version(
    dataset_key: str,
    dataset_version: str,
    slice_key: str,
    slice_version: str,
    db: Session = Depends(get_db),
) -> EvalDatasetSliceRead:
    item = get_eval_dataset_slice(dataset_key, dataset_version, slice_key, slice_version, db)
    if item is None:
        raise HTTPException(status_code=404, detail="Eval dataset slice not found")
    return serialize_eval_dataset_slice(item)


@app.delete(
    "/v1/eval-datasets/{dataset_key}/versions/{dataset_version}/slices/{slice_key}/versions/{slice_version}",
    status_code=204,
)
def delete_eval_dataset_slice_by_version(
    dataset_key: str,
    dataset_version: str,
    slice_key: str,
    slice_version: str,
    db: Session = Depends(get_db),
) -> None:
    try:
        delete_eval_dataset_slice(db, dataset_key, dataset_version, slice_key, slice_version)
    except EvalDatasetError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get(
    "/v1/eval-datasets/{dataset_key}/versions/{dataset_version}/grader-suites",
    response_model=list[GraderSuiteRead],
)
def get_grader_suites_route(
    dataset_key: str,
    dataset_version: str,
    db: Session = Depends(get_db),
) -> list[GraderSuiteRead]:
    return [
        serialize_grader_suite(item)
        for item in list_grader_suites(dataset_key, dataset_version, db)
    ]


@app.post(
    "/v1/eval-datasets/{dataset_key}/versions/{dataset_version}/grader-suites",
    response_model=GraderSuiteRead,
    status_code=201,
)
def create_grader_suite_route(
    dataset_key: str,
    dataset_version: str,
    payload: GraderSuiteWrite,
    db: Session = Depends(get_db),
) -> GraderSuiteRead:
    try:
        return serialize_grader_suite(create_grader_suite(db, dataset_key, dataset_version, payload))
    except (EvalDatasetError, GraderSuiteError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get(
    "/v1/eval-datasets/{dataset_key}/versions/{dataset_version}/grader-suites/{suite_key}/versions/{suite_version}",
    response_model=GraderSuiteRead,
)
def get_grader_suite_by_version(
    dataset_key: str,
    dataset_version: str,
    suite_key: str,
    suite_version: str,
    db: Session = Depends(get_db),
) -> GraderSuiteRead:
    suite = get_grader_suite(dataset_key, dataset_version, suite_key, suite_version, db)
    if suite is None:
        raise HTTPException(status_code=404, detail="Grader suite not found")
    return serialize_grader_suite(suite)


@app.delete(
    "/v1/eval-datasets/{dataset_key}/versions/{dataset_version}/grader-suites/{suite_key}/versions/{suite_version}",
    status_code=204,
)
def delete_grader_suite_by_version(
    dataset_key: str,
    dataset_version: str,
    suite_key: str,
    suite_version: str,
    db: Session = Depends(get_db),
) -> None:
    try:
        delete_grader_suite(db, dataset_key, dataset_version, suite_key, suite_version)
    except GraderSuiteError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post(
    "/v1/eval-datasets/{dataset_key}/versions/{dataset_version}/grader-suites/{suite_key}/versions/{suite_version}/runs",
    response_model=GraderSuiteRunRead,
)
def run_grader_suite_route(
    dataset_key: str,
    dataset_version: str,
    suite_key: str,
    suite_version: str,
    payload: GraderSuiteRunRequest,
    db: Session = Depends(get_db),
) -> GraderSuiteRunRead:
    try:
        return run_grader_suite(
            dataset_key=dataset_key,
            dataset_version=dataset_version,
            key=suite_key,
            version=suite_version,
            payload=payload,
            db=db,
        )
    except GraderSuiteError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post(
    "/v1/training-specs/{spec_key}/versions/{spec_version}/self-learning-cycle",
    response_model=SelfLearningCycleRead,
    status_code=201,
)
def run_self_learning_cycle_route(
    spec_key: str,
    spec_version: str,
    payload: SelfLearningCycleRequest,
) -> SelfLearningCycleRead:
    try:
        result = run_daily_self_learning_cycle(
            spec_key=spec_key,
            spec_version=spec_version,
            adapter_key=payload.adapter_key,
            adapter_version=payload.adapter_version,
            adapter_name=payload.adapter_name,
            adapter_description=payload.adapter_description,
            artifact_format=payload.artifact_format,
            comparison_report_file=payload.comparison_report_file,
            evaluator_artifact_files=payload.evaluator_artifact_files,
            grader_output_path=payload.grader_output_path,
            package_for_ollama=payload.package_for_ollama,
            ollama_model_name=payload.ollama_model_name,
            package_output_dir=payload.package_output_dir,
            temperature=payload.temperature,
            top_p=payload.top_p,
            system_prompt=payload.system_prompt,
            api_base_url=payload.api_base_url,
            trinity_root=payload.trinity_root,
            provenance=payload.provenance,
        )
    except (SelfLearningCycleError, FineTuningContractError, MlxLmWorkerError, OllamaPackagingError) as exc:
        status_code = 404 if "was not found" in str(exc) else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return SelfLearningCycleRead.model_validate(result.to_payload())


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


@app.post(
    "/v1/trinity/reply/policies/propose",
    response_model=TrinityReplyPolicyProposalRead,
)
def propose_trinity_reply_policy(
    payload: TrinityReplyPolicyProposalRequest,
) -> TrinityReplyPolicyProposalRead:
    try:
        return propose_reply_policy_from_bundle_files(
            learner_kind=payload.learner_kind,
            bundle_files=list(payload.bundle_files),
            eval_dataset_key=payload.eval_dataset_key,
            eval_dataset_version=payload.eval_dataset_version,
            eval_dataset_slice_key=payload.eval_dataset_slice_key,
            eval_dataset_slice_version=payload.eval_dataset_slice_version,
            baseline_policy_file=payload.baseline_policy_file,
            incumbent_policy_file=payload.incumbent_policy_file,
            proposal_output_path=payload.proposal_output_path,
            eval_output_path=payload.eval_output_path,
            comparison_output_path=payload.comparison_output_path,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post(
    "/v1/trinity/spot/policies/propose",
    response_model=TrinitySpotPolicyProposalRead,
)
def propose_trinity_spot_policy(
    payload: TrinitySpotPolicyProposalRequest,
) -> TrinitySpotPolicyProposalRead:
    try:
        return propose_spot_review_policy_from_bundle_files(
            learner_kind=payload.learner_kind,
            bundle_files=list(payload.bundle_files),
            eval_dataset_key=payload.eval_dataset_key,
            eval_dataset_version=payload.eval_dataset_version,
            eval_dataset_slice_key=payload.eval_dataset_slice_key,
            eval_dataset_slice_version=payload.eval_dataset_slice_version,
            proposal_output_path=payload.proposal_output_path,
            eval_output_path=payload.eval_output_path,
            comparison_output_path=payload.comparison_output_path,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post(
    "/v1/trinity/reviews/skeptical-eval",
    response_model=TrinitySkepticalEvalRead,
)
def build_trinity_skeptical_eval(
    payload: TrinitySkepticalEvalRequest,
) -> TrinitySkepticalEvalRead:
    try:
        return build_skeptical_eval_report(
            component_key=payload.component_key,
            artifact_family=payload.artifact_family,
            proposal_artifact_version=payload.proposal_artifact_version,
            proposal_ref=payload.proposal_ref,
            comparison_report_file=payload.comparison_report_file,
            review_scope_kind=payload.review_scope_kind,
            review_scope_value=payload.review_scope_value,
            minimum_sample_count=payload.minimum_sample_count,
            minimum_improvement_delta=payload.minimum_improvement_delta,
            hidden_confounds=payload.hidden_confounds,
            overfitting_risks=payload.overfitting_risks,
            weak_assumptions=payload.weak_assumptions,
            disconfirming_signals=payload.disconfirming_signals,
            additional_rejection_evidence=payload.additional_rejection_evidence,
            additional_disproof_tests=payload.additional_disproof_tests,
            skeptical_eval_output_path=payload.skeptical_eval_output_path,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


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
