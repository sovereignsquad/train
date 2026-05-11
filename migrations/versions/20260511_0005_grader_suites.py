"""grader suites

Revision ID: 20260511_0005
Revises: 20260511_0004
Create Date: 2026-05-11 09:05:00
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260511_0005"
down_revision: str | None = "20260511_0004"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "grader_suites" not in table_names:
        op.create_table(
            "grader_suites",
            sa.Column("dataset_key", sa.String(length=120), nullable=False),
            sa.Column("dataset_version", sa.String(length=160), nullable=False),
            sa.Column("key", sa.String(length=120), nullable=False),
            sa.Column("version", sa.String(length=160), nullable=False),
            sa.Column("name", sa.String(length=200), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("proposal_family", sa.String(length=120), nullable=False),
            sa.Column("graders_json", sa.Text(), nullable=False),
            sa.Column("provenance_json", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("dataset_key", "dataset_version", "key", "version"),
        )
        op.create_index(
            "ix_grader_suites_proposal_family",
            "grader_suites",
            ["proposal_family"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "grader_suites" in table_names:
        op.drop_index("ix_grader_suites_proposal_family", table_name="grader_suites")
        op.drop_table("grader_suites")
