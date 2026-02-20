"""initial multitenant schema

Revision ID: 20260220_0001
Revises:
Create Date: 2026-02-20 00:00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260220_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


user_role = sa.Enum("admin", "manager", "reviewer", name="user_role")
campaign_state = sa.Enum("draft", "active", "paused", "archived", name="campaign_state")


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_tenants_id"), "tenants", ["id"], unique=False)

    user_role.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_tenant_id"), "users", ["tenant_id"], unique=False)

    campaign_state.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "campaigns",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("state", campaign_state, nullable=False, server_default="draft"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_campaigns_id"), "campaigns", ["id"], unique=False)
    op.create_index(op.f("ix_campaigns_tenant_id"), "campaigns", ["tenant_id"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("previous_state", sa.JSON(), nullable=True),
        sa.Column("new_state", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_id"), "audit_logs", ["id"], unique=False)
    op.create_index(op.f("ix_audit_logs_tenant_id"), "audit_logs", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_logs_tenant_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_id"), table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index(op.f("ix_campaigns_tenant_id"), table_name="campaigns")
    op.drop_index(op.f("ix_campaigns_id"), table_name="campaigns")
    op.drop_table("campaigns")
    campaign_state.drop(op.get_bind(), checkfirst=True)

    op.drop_index(op.f("ix_users_tenant_id"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
    user_role.drop(op.get_bind(), checkfirst=True)

    op.drop_index(op.f("ix_tenants_id"), table_name="tenants")
    op.drop_table("tenants")
