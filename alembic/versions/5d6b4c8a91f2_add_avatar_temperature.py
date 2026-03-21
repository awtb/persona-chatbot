"""Add avatar temperature

Revision ID: 5d6b4c8a91f2
Revises: 6c41a059cb91
Create Date: 2026-03-21 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "5d6b4c8a91f2"
down_revision: Union[str, Sequence[str], None] = "6c41a059cb91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "avatars",
        sa.Column("temperature", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("avatars", "temperature")
