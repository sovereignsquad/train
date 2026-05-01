"""managed projects

Revision ID: 20260430_0003
Revises: 20260430_0002
Create Date: 2026-04-30 20:55:00
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260430_0003"
down_revision: str | None = "20260430_0002"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "managed_projects" not in table_names:
        op.create_table(
            "managed_projects",
            sa.Column("key", sa.String(length=120), primary_key=True),
            sa.Column("name", sa.String(length=200), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("mutable_artifact", sa.String(length=260), nullable=False),
            sa.Column("autonomous_mutable_artifacts_json", sa.Text(), nullable=False),
            sa.Column("setup_artifacts_json", sa.Text(), nullable=False),
            sa.Column("dependency_artifacts_json", sa.Text(), nullable=False),
            sa.Column(
                "metric_direction",
                sa.Enum("MINIMIZE", "MAXIMIZE", name="metricdirection"),
                nullable=False,
            ),
            sa.Column("metric_name", sa.String(length=120), nullable=False),
            sa.Column("min_budget_seconds", sa.Integer(), nullable=False),
            sa.Column("default_budget_seconds", sa.Integer(), nullable=False),
            sa.Column("max_budget_seconds", sa.Integer(), nullable=False),
            sa.Column("runner_key", sa.String(length=120), nullable=False),
            sa.Column("execution_entrypoint", sa.String(length=260), nullable=False),
            sa.Column("template_key", sa.String(length=120), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "managed_projects" in table_names:
        op.drop_table("managed_projects")
