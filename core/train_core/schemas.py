from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from train_core.agents import AgentMode
from train_core.models import GitAction, MetricDirection, RatchetDecision, RunStatus
from train_core.providers import ProviderKind

TRINITY_REPLY_ADAPTER_NAME = "reply"
TRINITY_REPLY_ADAPTER_CONTRACT_PREFIX = "trinity.reply."


class ReplyTonePreferencesProposal(BaseModel):
    target_tone: str = Field(min_length=1, max_length=80)
    formality: str = Field(min_length=1, max_length=40)
    warmth: str = Field(min_length=1, max_length=40)
    directness: str = Field(min_length=1, max_length=40)
    forbidden_tones: tuple[str, ...] = ()


class ReplyBrevityPreferencesProposal(BaseModel):
    target_length: str = Field(min_length=1, max_length=40)
    max_sentences: int | None = Field(default=None, ge=1)
    max_chars: int | None = Field(default=None, ge=1)
    prefer_single_paragraph: bool = True


class ReplyChannelRulesProposal(BaseModel):
    opening_style: str = Field(min_length=1, max_length=80)
    closing_style: str = Field(min_length=1, max_length=80)
    emoji_policy: str = Field(min_length=1, max_length=40)
    url_policy: str = Field(min_length=1, max_length=40)
    attachment_reference_policy: str = Field(min_length=1, max_length=80)
    newline_policy: str = Field(min_length=1, max_length=80)


class ReplyBehaviorPolicyProposal(BaseModel):
    artifact_key: str = Field(min_length=1, max_length=120)
    version: str = Field(min_length=1, max_length=160)
    scope_kind: str = Field(min_length=1, max_length=40)
    scope_value: str | None = None
    created_at: datetime
    source_project: str = Field(min_length=1, max_length=120)
    tone_preferences: ReplyTonePreferencesProposal
    brevity_preferences: ReplyBrevityPreferencesProposal
    channel_rules: ReplyChannelRulesProposal
    notes: str | None = None
    contract_version: str = Field(min_length=1, max_length=120)

    @model_validator(mode="after")
    def validate_policy_scope(self) -> "ReplyBehaviorPolicyProposal":
        if self.scope_kind not in {"global", "company", "channel"}:
            raise ValueError("Reply behavior policy scope_kind is invalid")
        if self.scope_kind == "global" and self.scope_value is not None:
            raise ValueError("Global reply behavior policy must not set scope_value")
        if self.scope_kind in {"company", "channel"} and not self.scope_value:
            raise ValueError("Company and channel reply behavior policy require scope_value")
        if not _is_reply_adapter_contract_version(self.contract_version):
            raise ValueError("Reply behavior policy contract_version is invalid")
        return self


class TrinityReplyPolicyProposalRequest(BaseModel):
    learner_kind: str = Field(min_length=1, max_length=80)
    bundle_files: tuple[str, ...] = Field(min_length=1)
    baseline_policy_file: str | None = None
    incumbent_policy_file: str | None = None
    proposal_output_path: str | None = None
    eval_output_path: str | None = None
    comparison_output_path: str | None = None

    @model_validator(mode="after")
    def validate_request(self) -> "TrinityReplyPolicyProposalRequest":
        if self.learner_kind not in {"tone", "brevity", "channel-formatting"}:
            raise ValueError("learner_kind is invalid")
        return self


class TrinityReplyPolicyProposalRead(BaseModel):
    learner_kind: str = Field(min_length=1, max_length=80)
    bundle_count: int = Field(ge=1)
    proposal: ReplyBehaviorPolicyProposal
    eval_report: dict[str, object]
    comparison_report: dict[str, object] | None = None
    proposal_path: str | None = None
    eval_output_path: str | None = None
    comparison_output_path: str | None = None


class RunCreate(BaseModel):
    project_key: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=200)
    objective: str | None = None
    metric_name: str | None = Field(default=None, max_length=120)
    metric_direction: MetricDirection | None = None
    budget_seconds: int | None = Field(default=None, ge=1, le=86_400)


class RunStart(BaseModel):
    pass


class RunHeartbeat(BaseModel):
    lease_seconds: int | None = Field(default=None, ge=5, le=86_400)


class RunComplete(BaseModel):
    status: RunStatus
    metric_value: float | None = None
    result_summary: str | None = None
    error_message: str | None = None

    @model_validator(mode="after")
    def validate_terminal_payload(self) -> "RunComplete":
        if self.status not in {RunStatus.SUCCEEDED, RunStatus.FAILED, RunStatus.ACCEPTED, RunStatus.REJECTED}:
            raise ValueError("Completion status must be a terminal run status")
        if self.status in {RunStatus.SUCCEEDED, RunStatus.ACCEPTED, RunStatus.REJECTED} and self.metric_value is None:
            raise ValueError("A metric value is required for successful terminal statuses")
        if self.status == RunStatus.FAILED and not self.error_message:
            raise ValueError("An error message is required when marking a run as failed")
        return self


class ProjectRead(BaseModel):
    key: str
    name: str
    description: str
    mutable_artifact: str
    autonomous_mutable_artifacts: tuple[str, ...]
    setup_artifacts: tuple[str, ...]
    dependency_artifacts: tuple[str, ...]
    metric_name: str
    metric_direction: MetricDirection
    min_budget_seconds: int
    default_budget_seconds: int
    max_budget_seconds: int
    runner_key: str
    execution_entrypoint: str
    source_kind: str
    editable: bool
    deletable: bool
    template_key: str | None


class ProjectWrite(BaseModel):
    key: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    mutable_artifact: str = Field(min_length=1, max_length=260)
    autonomous_mutable_artifacts: tuple[str, ...] = Field(min_length=1)
    setup_artifacts: tuple[str, ...] = Field(min_length=1)
    dependency_artifacts: tuple[str, ...] = Field(min_length=1)
    metric_name: str = Field(min_length=1, max_length=120)
    metric_direction: MetricDirection
    min_budget_seconds: int = Field(ge=1, le=86_400)
    default_budget_seconds: int = Field(ge=1, le=86_400)
    max_budget_seconds: int = Field(ge=1, le=86_400)
    runner_key: str = Field(min_length=1, max_length=120)
    execution_entrypoint: str = Field(min_length=1, max_length=260)
    template_key: str | None = Field(default=None, max_length=120)

    @model_validator(mode="after")
    def validate_project_budgets(self) -> "ProjectWrite":
        if self.min_budget_seconds > self.default_budget_seconds:
            raise ValueError("Default budget must be greater than or equal to min budget")
        if self.default_budget_seconds > self.max_budget_seconds:
            raise ValueError("Default budget must be less than or equal to max budget")
        return self


class ProjectBootstrapRequest(BaseModel):
    overwrite: bool = False


class ProjectBootstrapRead(BaseModel):
    project_key: str
    project_root: str
    created_files: tuple[str, ...]
    overwritten_files: tuple[str, ...]
    skipped_files: tuple[str, ...]


class ExecutionResult(BaseModel):
    status: RunStatus
    metric_value: float | None = None
    result_summary: str | None = None
    error_message: str | None = None


class RunRead(BaseModel):
    id: int
    project_key: str
    title: str
    objective: str | None
    metric_name: str | None
    metric_direction: MetricDirection
    metric_value: float | None
    budget_seconds: int
    status: RunStatus
    mutable_artifact: str | None
    runner_key: str | None
    ratchet_decision: RatchetDecision
    git_action: GitAction
    best_metric_before: float | None
    best_metric_after: float | None
    git_head_before: str | None
    git_head_after: str | None
    git_worktree_dirty: bool | None
    started_at: datetime | None
    heartbeat_at: datetime | None
    lease_expires_at: datetime | None
    finished_at: datetime | None
    resumed_from_run_id: int | None
    resume_count: int
    result_summary: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecoverableRunRead(BaseModel):
    id: int
    project_key: str
    title: str
    status: RunStatus
    stalled: bool
    resumable: bool
    resume_count: int
    resumed_from_run_id: int | None
    heartbeat_at: datetime | None
    lease_expires_at: datetime | None
    best_run_id: int | None
    checkpoint_git_head: str | None
    error_message: str | None
    updated_at: datetime

    model_config = {"from_attributes": True}


class OperatorStatusRead(BaseModel):
    generated_at: datetime
    total_runs: int
    running_runs: int
    healthy_running_runs: int
    stalled_runs: int
    recoverable_runs: list[RecoverableRunRead]

    model_config = {"from_attributes": True}


class ProjectStateRead(BaseModel):
    project_key: str
    metric_name: str
    metric_direction: MetricDirection
    best_run_id: int | None
    best_metric_value: float | None
    last_run_id: int | None
    git_head: str | None
    git_worktree_dirty: bool | None
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentAdapterRead(BaseModel):
    key: str
    name: str
    description: str
    executable: str
    first_class: bool


class AgentStatusRead(BaseModel):
    key: str
    name: str
    available: bool
    executable: str
    resolved_executable: str | None
    version: str | None
    mistral_api_key_configured: bool
    contract_home: str
    runtime_home: str
    config_path: str
    agent_config_path: str
    prompt_path: str
    issues: list[str]


class AgentLaunchPlanRead(BaseModel):
    adapter_key: str
    project_key: str
    mode: AgentMode
    command: list[str]
    prompt: str
    workdir: str
    environment: dict[str, str]
    summary: str


class ProviderAdapterRead(BaseModel):
    key: str
    name: str
    kind: ProviderKind
    description: str
    base_url: str
    requires_api_key: bool


class ProviderStatusRead(BaseModel):
    key: str
    name: str
    kind: ProviderKind
    base_url: str
    configured: bool
    reachable: bool
    model_count: int | None
    models: tuple[str, ...]
    issues: list[str]


class TrinityAcceptedArtifactVersion(BaseModel):
    artifact_key: str = Field(min_length=1, max_length=120)
    version: str = Field(min_length=1, max_length=120)
    source_project: str = Field(min_length=1, max_length=120)
    accepted_at: datetime


class TrinityReplyDraftOutcome(BaseModel):
    company_id: str = Field(min_length=1, max_length=80)
    cycle_id: str = Field(min_length=1, max_length=80)
    thread_ref: str = Field(min_length=1)
    channel: str = Field(min_length=1, max_length=40)
    disposition: str = Field(min_length=1, max_length=80)
    occurred_at: datetime
    candidate_id: str | None = None
    original_draft_text: str | None = None
    final_text: str | None = None
    edit_distance: float | None = Field(default=None, ge=0.0, le=1.0)
    latency_ms: int | None = Field(default=None, ge=0)
    send_result: str | None = None
    notes: str | None = None


class TrinityThreadMessageSnapshot(BaseModel):
    message_id: str = Field(min_length=1)
    role: str = Field(min_length=1, max_length=40)
    text: str = Field(min_length=1)
    occurred_at: datetime
    channel: str = Field(min_length=1, max_length=40)
    source: str = Field(min_length=1, max_length=80)
    handle: str = Field(min_length=1)


class TrinityThreadContextSnippet(BaseModel):
    source: str = Field(min_length=1, max_length=120)
    path: str = Field(min_length=1)
    text: str = Field(min_length=1)


class TrinityGoldenExample(BaseModel):
    path: str = Field(min_length=1)
    text: str = Field(min_length=1)


class TrinityThreadSnapshotRecord(BaseModel):
    company_id: str = Field(min_length=1, max_length=80)
    thread_ref: str = Field(min_length=1)
    channel: str = Field(min_length=1, max_length=40)
    contact_handle: str = Field(min_length=1)
    latest_inbound_text: str = Field(min_length=1)
    requested_at: datetime
    messages: tuple[TrinityThreadMessageSnapshot, ...] = ()
    context_snippets: tuple[TrinityThreadContextSnippet, ...] = ()
    golden_examples: tuple[TrinityGoldenExample, ...] = ()
    metadata: dict[str, str] = Field(default_factory=dict)
    contract_version: str = Field(min_length=1, max_length=120)

    @model_validator(mode="after")
    def validate_contract_version(self) -> "TrinityThreadSnapshotRecord":
        if not _is_reply_adapter_contract_version(self.contract_version):
            raise ValueError("Thread snapshot contract_version is invalid")
        return self


class TrinityEvidenceSourceRef(BaseModel):
    external_id: str = Field(min_length=1)
    locator: str | None = None
    version: str | None = None


class TrinityEvidenceUnitRecord(BaseModel):
    company_id: str = Field(min_length=1, max_length=80)
    evidence_id: str = Field(min_length=1, max_length=80)
    source_type: str = Field(min_length=1, max_length=80)
    source_ref: TrinityEvidenceSourceRef
    content_raw: str = Field(min_length=1)
    content_canonical: str = Field(min_length=1)
    content_hash: str = Field(min_length=1, max_length=128)
    metadata: dict[str, str] = Field(default_factory=dict)
    topic_hints: tuple[str, ...] = ()
    created_at: datetime
    updated_at: datetime


class TrinityCandidateScoresRecord(BaseModel):
    impact: int
    confidence: int
    ease: int
    quality_score: float
    urgency_score: float
    freshness_score: float
    feedback_score: float


class TrinityRankedDraftCandidateRecord(BaseModel):
    company_id: str = Field(min_length=1, max_length=80)
    candidate_id: str = Field(min_length=1, max_length=80)
    thread_ref: str = Field(min_length=1)
    recipient_handle: str = Field(min_length=1)
    channel: str = Field(min_length=1, max_length=40)
    rank: int = Field(ge=1)
    draft_text: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    risk_flags: tuple[str, ...] = ()
    delivery_eligible: bool
    scores: TrinityCandidateScoresRecord
    source_evidence_ids: tuple[str, ...] = Field(min_length=1)
    candidate_type: str = Field(min_length=1, max_length=80)
    contract_version: str = Field(min_length=1, max_length=120)

    @model_validator(mode="after")
    def validate_contract_version(self) -> "TrinityRankedDraftCandidateRecord":
        if not _is_reply_adapter_contract_version(self.contract_version):
            raise ValueError("Ranked draft candidate contract_version is invalid")
        return self


class TrinityRankedDraftSetRecord(BaseModel):
    cycle_id: str = Field(min_length=1, max_length=80)
    thread_ref: str = Field(min_length=1)
    channel: str = Field(min_length=1, max_length=40)
    generated_at: datetime
    drafts: tuple[TrinityRankedDraftCandidateRecord, ...] = Field(min_length=1)
    accepted_artifact_version: TrinityAcceptedArtifactVersion
    trace_ref: str | None = None
    contract_version: str = Field(min_length=1, max_length=120)

    @model_validator(mode="after")
    def validate_contract_version(self) -> "TrinityRankedDraftSetRecord":
        if not _is_reply_adapter_contract_version(self.contract_version):
            raise ValueError("Ranked draft set contract_version is invalid")
        return self


class TrinityReplyTraceRecord(BaseModel):
    contract_version: str = Field(min_length=1, max_length=120)
    cycle_id: str = Field(min_length=1, max_length=80)
    exported_at: datetime
    snapshot_hash: str = Field(min_length=1, max_length=128)
    frontier_candidate_ids: tuple[str, ...] = Field(min_length=1)
    feedback_events: tuple[TrinityReplyDraftOutcome, ...] = ()
    model_routes: dict[str, str] = Field(default_factory=dict)
    accepted_artifact_version: TrinityAcceptedArtifactVersion

    @model_validator(mode="after")
    def validate_contract_version(self) -> "TrinityReplyTraceRecord":
        if not _is_reply_adapter_contract_version(self.contract_version):
            raise ValueError("Trinity reply trace contract_version is invalid")
        return self


class TrinityTrainingBundleRecord(BaseModel):
    bundle_id: str = Field(min_length=1, max_length=80)
    bundle_type: str = Field(min_length=1, max_length=120)
    exported_at: datetime
    thread_snapshot: TrinityThreadSnapshotRecord
    evidence_units: tuple[TrinityEvidenceUnitRecord, ...]
    ranked_draft_set: TrinityRankedDraftSetRecord
    selected_candidate_id: str | None = None
    draft_outcome_event: TrinityReplyDraftOutcome
    labels: dict[str, str] = Field(default_factory=dict)
    contract_version: str = Field(min_length=1, max_length=120)

    @model_validator(mode="after")
    def validate_bundle(self) -> "TrinityTrainingBundleRecord":
        if not _is_reply_adapter_contract_version(self.contract_version):
            raise ValueError("Training bundle contract_version is invalid")
        allowed_bundle_types = {
            "tone-learning",
            "brevity-learning",
            "channel-formatting-learning",
        }
        if self.bundle_type not in allowed_bundle_types:
            raise ValueError("Training bundle type is invalid")
        if self.selected_candidate_id is not None:
            ranked_candidate_ids = {draft.candidate_id for draft in self.ranked_draft_set.drafts}
            if self.selected_candidate_id not in ranked_candidate_ids:
                raise ValueError("selected_candidate_id must exist in ranked_draft_set.drafts")
        return self


def _is_reply_adapter_contract_version(contract_version: str) -> bool:
    return str(contract_version or "").startswith(TRINITY_REPLY_ADAPTER_CONTRACT_PREFIX)
