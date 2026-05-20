"""fine tuning contracts

Revision ID: 20260513_0006
Revises: 20260511_0005
Create Date: 2026-05-13 10:30:00
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260513_0006"
down_revision: str | None = "20260511_0005"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "training_specs" not in table_names:
        op.create_table(
            "training_specs",
            sa.Column("key", sa.String(length=120), nullable=False),
            sa.Column("version", sa.String(length=160), nullable=False),
            sa.Column("name", sa.String(length=200), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("dataset_key", sa.String(length=120), nullable=False),
            sa.Column("dataset_version", sa.String(length=160), nullable=False),
            sa.Column("dataset_slice_key", sa.String(length=120), nullable=True),
            sa.Column("dataset_slice_version", sa.String(length=160), nullable=True),
            sa.Column("grader_suite_key", sa.String(length=120), nullable=False),
            sa.Column("grader_suite_version", sa.String(length=160), nullable=False),
            sa.Column("base_model_ref", sa.String(length=260), nullable=False),
            sa.Column("template_ref", sa.String(length=260), nullable=False),
            sa.Column("tokenizer_ref", sa.String(length=260), nullable=True),
            sa.Column("training_backend", sa.String(length=40), nullable=False),
            sa.Column("training_stage", sa.String(length=40), nullable=False),
            sa.Column("training_method", sa.String(length=40), nullable=False),
            sa.Column("expected_adapter_family", sa.String(length=120), nullable=False),
            sa.Column("output_dir", sa.String(length=520), nullable=False),
            sa.Column("hyperparameters_json", sa.Text(), nullable=False),
            sa.Column("provenance_json", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("key", "version"),
        )
        op.create_index(
            "ix_training_specs_dataset_key",
            "training_specs",
            ["dataset_key"],
            unique=False,
        )
        op.create_index(
            "ix_training_specs_training_backend",
            "training_specs",
            ["training_backend"],
            unique=False,
        )
        op.create_index(
            "ix_training_specs_expected_adapter_family",
            "training_specs",
            ["expected_adapter_family"],
            unique=False,
        )

    if "adapter_artifacts" not in table_names:
        op.create_table(
            "adapter_artifacts",
            sa.Column("key", sa.String(length=120), nullable=False),
            sa.Column("version", sa.String(length=160), nullable=False),
            sa.Column("training_spec_key", sa.String(length=120), nullable=False),
            sa.Column("training_spec_version", sa.String(length=160), nullable=False),
            sa.Column("name", sa.String(length=200), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("dataset_key", sa.String(length=120), nullable=False),
            sa.Column("dataset_version", sa.String(length=160), nullable=False),
            sa.Column("dataset_slice_key", sa.String(length=120), nullable=True),
            sa.Column("dataset_slice_version", sa.String(length=160), nullable=True),
            sa.Column("grader_suite_key", sa.String(length=120), nullable=False),
            sa.Column("grader_suite_version", sa.String(length=160), nullable=False),
            sa.Column("base_model_ref", sa.String(length=260), nullable=False),
            sa.Column("template_ref", sa.String(length=260), nullable=False),
            sa.Column("tokenizer_ref", sa.String(length=260), nullable=True),
            sa.Column("training_backend", sa.String(length=40), nullable=False),
            sa.Column("training_stage", sa.String(length=40), nullable=False),
            sa.Column("training_method", sa.String(length=40), nullable=False),
            sa.Column("adapter_family", sa.String(length=120), nullable=False),
            sa.Column("adapter_format", sa.String(length=40), nullable=False),
            sa.Column("artifact_path", sa.String(length=520), nullable=False),
            sa.Column("checkpoint_path", sa.String(length=520), nullable=True),
            sa.Column("training_log_path", sa.String(length=520), nullable=True),
            sa.Column("packaging_metadata_path", sa.String(length=520), nullable=True),
            sa.Column("provenance_json", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("key", "version"),
        )
        op.create_index(
            "ix_adapter_artifacts_training_spec_key",
            "adapter_artifacts",
            ["training_spec_key"],
            unique=False,
        )
        op.create_index(
            "ix_adapter_artifacts_dataset_key",
            "adapter_artifacts",
            ["dataset_key"],
            unique=False,
        )
        op.create_index(
            "ix_adapter_artifacts_training_backend",
            "adapter_artifacts",
            ["training_backend"],
            unique=False,
        )
        op.create_index(
            "ix_adapter_artifacts_adapter_family",
            "adapter_artifacts",
            ["adapter_family"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_names = set(inspector.get_table_names())

    if "adapter_artifacts" in table_names:
        op.drop_index("ix_adapter_artifacts_adapter_family", table_name="adapter_artifacts")
        op.drop_index("ix_adapter_artifacts_training_backend", table_name="adapter_artifacts")
        op.drop_index("ix_adapter_artifacts_dataset_key", table_name="adapter_artifacts")
        op.drop_index("ix_adapter_artifacts_training_spec_key", table_name="adapter_artifacts")
        op.drop_table("adapter_artifacts")

    if "training_specs" in table_names:
        op.drop_index("ix_training_specs_expected_adapter_family", table_name="training_specs")
        op.drop_index("ix_training_specs_training_backend", table_name="training_specs")
        op.drop_index("ix_training_specs_dataset_key", table_name="training_specs")
        op.drop_table("training_specs")
