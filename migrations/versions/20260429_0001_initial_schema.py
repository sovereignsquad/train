"""initial schema

Revision ID: 20260429_0001
Revises:
Create Date: 2026-04-29 17:00:00
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260429_0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


metric_direction_enum = sa.Enum("MINIMIZE", "MAXIMIZE", name="metricdirection")
run_status_enum = sa.Enum(
    "PENDING",
    "RUNNING",
    "SUCCEEDED",
    "FAILED",
    "ACCEPTED",
    "REJECTED",
    name="runstatus",
)
ratchet_decision_enum = sa.Enum(
    "ACCEPTED",
    "REJECTED",
    "NOT_APPLICABLE",
    name="ratchetdecision",
)
git_action_enum = sa.Enum(
    "NONE",
    "COMMITTED",
    "RESTORED",
    "BLOCKED",
    name="gitaction",
)


def upgrade() -> None:
    op.create_table(
        "project_states",
        sa.Column("project_key", sa.String(length=120), nullable=False),
        sa.Column("metric_name", sa.String(length=120), nullable=False),
        sa.Column("metric_direction", metric_direction_enum, nullable=False),
        sa.Column("best_run_id", sa.Integer(), nullable=True),
        sa.Column("best_metric_value", sa.Float(), nullable=True),
        sa.Column("last_run_id", sa.Integer(), nullable=True),
        sa.Column("git_head", sa.String(length=120), nullable=True),
        sa.Column("git_worktree_dirty", sa.Boolean(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("project_key"),
    )
    op.create_table(
        "run_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_key", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("objective", sa.Text(), nullable=True),
        sa.Column("metric_name", sa.String(length=120), nullable=True),
        sa.Column("metric_direction", metric_direction_enum, nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=True),
        sa.Column("budget_seconds", sa.Integer(), nullable=False),
        sa.Column("status", run_status_enum, nullable=False),
        sa.Column("mutable_artifact", sa.String(length=260), nullable=True),
        sa.Column("runner_key", sa.String(length=120), nullable=True),
        sa.Column("ratchet_decision", ratchet_decision_enum, nullable=False),
        sa.Column("git_action", git_action_enum, nullable=False),
        sa.Column("best_metric_before", sa.Float(), nullable=True),
        sa.Column("best_metric_after", sa.Float(), nullable=True),
        sa.Column("git_head_before", sa.String(length=120), nullable=True),
        sa.Column("git_head_after", sa.String(length=120), nullable=True),
        sa.Column("git_worktree_dirty", sa.Boolean(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("result_summary", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_run_records_id"), "run_records", ["id"], unique=False)
    op.create_index(op.f("ix_run_records_project_key"), "run_records", ["project_key"], unique=False)
    op.create_index(op.f("ix_run_records_status"), "run_records", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_run_records_status"), table_name="run_records")
    op.drop_index(op.f("ix_run_records_project_key"), table_name="run_records")
    op.drop_index(op.f("ix_run_records_id"), table_name="run_records")
    op.drop_table("run_records")
    op.drop_table("project_states")
