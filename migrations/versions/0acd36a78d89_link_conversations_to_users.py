"""link conversations to users

Revision ID: 0acd36a78d89
Revises: 7dc4f5f0b8c8
Create Date: 2026-09-25 00:38:24.023165

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0acd36a78d89'
down_revision: Union[str, Sequence[str], None] = '7dc4f5f0b8c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "conversations",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )

    # Existing integration-test conversations belong to test user 1.
    op.execute(
        "UPDATE conversations SET user_id = 1 WHERE user_id IS NULL"
    )

    op.alter_column(
        "conversations",
        "user_id",
        nullable=False,
    )

    op.create_index(
        op.f("ix_conversations_user_id"),
        "conversations",
        ["user_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_conversations_user_id_users",
        "conversations",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_conversations_user_id_users",
        "conversations",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_conversations_user_id"),
        table_name="conversations",
    )

    op.drop_column(
        "conversations",
        "user_id",
    )
