"""enable pgvector

Revision ID: 1a9a85b8d55c
Revises: 040c3d105cfd
Create Date: 2026-09-25
"""

from typing import Sequence, Union

from alembic import op


revision: str = "1a9a85b8d55c"
down_revision: Union[str, Sequence[str], None] = "040c3d105cfd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Enable the PostgreSQL vector extension."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    """Disable the PostgreSQL vector extension."""
    op.execute("DROP EXTENSION IF EXISTS vector")
