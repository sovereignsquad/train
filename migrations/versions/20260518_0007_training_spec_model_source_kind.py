"""training spec model source kind

Revision ID: 20260518_0007
Revises: 20260513_0006
Create Date: 2026-05-18 12:00:00
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260518_0007"
down_revision: str | None = "20260513_0006"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "training_specs" in table_names:
        columns = {column["name"] for column in inspector.get_columns("training_specs")}
        if "base_model_source_kind" not in columns:
            op.add_column(
                "training_specs",
                sa.Column(
                    "base_model_source_kind",
                    sa.String(length=40),
                    nullable=False,
                    server_default="huggingface",
                ),
            )

    if "adapter_artifacts" in table_names:
        columns = {column["name"] for column in inspector.get_columns("adapter_artifacts")}
        if "base_model_source_kind" not in columns:
            op.add_column(
                "adapter_artifacts",
                sa.Column(
                    "base_model_source_kind",
                    sa.String(length=40),
                    nullable=False,
                    server_default="huggingface",
                ),
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "adapter_artifacts" in table_names:
        columns = {column["name"] for column in inspector.get_columns("adapter_artifacts")}
        if "base_model_source_kind" in columns:
            op.drop_column("adapter_artifacts", "base_model_source_kind")

    if "training_specs" in table_names:
        columns = {column["name"] for column in inspector.get_columns("training_specs")}
        if "base_model_source_kind" in columns:
            op.drop_column("training_specs", "base_model_source_kind")
