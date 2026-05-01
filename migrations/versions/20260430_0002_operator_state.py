"""operator state

Revision ID: 20260430_0002
Revises: 20260429_0001
Create Date: 2026-04-30 09:00:00
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260430_0002"
down_revision: str | None = "20260429_0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = {column["name"] for column in inspector.get_columns("run_records")}

    if "heartbeat_at" not in existing:
        op.add_column("run_records", sa.Column("heartbeat_at", sa.DateTime(), nullable=True))
    if "lease_expires_at" not in existing:
        op.add_column("run_records", sa.Column("lease_expires_at", sa.DateTime(), nullable=True))
    if "resumed_from_run_id" not in existing:
        op.add_column("run_records", sa.Column("resumed_from_run_id", sa.Integer(), nullable=True))
    if "resume_count" not in existing:
        op.add_column(
            "run_records",
            sa.Column("resume_count", sa.Integer(), nullable=False, server_default="0"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = {column["name"] for column in inspector.get_columns("run_records")}

    if "resume_count" in existing:
        op.drop_column("run_records", "resume_count")
    if "resumed_from_run_id" in existing:
        op.drop_column("run_records", "resumed_from_run_id")
    if "lease_expires_at" in existing:
        op.drop_column("run_records", "lease_expires_at")
    if "heartbeat_at" in existing:
        op.drop_column("run_records", "heartbeat_at")
