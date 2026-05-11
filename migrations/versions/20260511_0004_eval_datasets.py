"""eval datasets

Revision ID: 20260511_0004
Revises: 20260430_0003
Create Date: 2026-05-11 08:20:00
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260511_0004"
down_revision: str | None = "20260430_0003"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "eval_datasets" not in table_names:
        op.create_table(
            "eval_datasets",
            sa.Column("key", sa.String(length=120), nullable=False),
            sa.Column("version", sa.String(length=160), nullable=False),
            sa.Column("name", sa.String(length=200), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("source_kind", sa.String(length=40), nullable=False),
            sa.Column("scope_kind", sa.String(length=40), nullable=False),
            sa.Column("scope_value", sa.String(length=120), nullable=True),
            sa.Column("items_json", sa.Text(), nullable=False),
            sa.Column("provenance_json", sa.Text(), nullable=False),
            sa.Column("item_count", sa.Integer(), nullable=False),
            sa.Column("fingerprint", sa.String(length=64), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("key", "version"),
        )
        op.create_index("ix_eval_datasets_fingerprint", "eval_datasets", ["fingerprint"], unique=False)

    if "eval_dataset_slices" not in table_names:
        op.create_table(
            "eval_dataset_slices",
            sa.Column("dataset_key", sa.String(length=120), nullable=False),
            sa.Column("dataset_version", sa.String(length=160), nullable=False),
            sa.Column("key", sa.String(length=120), nullable=False),
            sa.Column("version", sa.String(length=160), nullable=False),
            sa.Column("name", sa.String(length=200), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("scope_kind", sa.String(length=40), nullable=False),
            sa.Column("scope_value", sa.String(length=120), nullable=True),
            sa.Column("selection_item_keys_json", sa.Text(), nullable=False),
            sa.Column("provenance_json", sa.Text(), nullable=False),
            sa.Column("item_count", sa.Integer(), nullable=False),
            sa.Column("fingerprint", sa.String(length=64), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("dataset_key", "dataset_version", "key", "version"),
        )
        op.create_index(
            "ix_eval_dataset_slices_fingerprint",
            "eval_dataset_slices",
            ["fingerprint"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "eval_dataset_slices" in table_names:
        op.drop_index("ix_eval_dataset_slices_fingerprint", table_name="eval_dataset_slices")
        op.drop_table("eval_dataset_slices")
    if "eval_datasets" in table_names:
        op.drop_index("ix_eval_datasets_fingerprint", table_name="eval_datasets")
        op.drop_table("eval_datasets")
