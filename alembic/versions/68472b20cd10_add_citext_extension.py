"""add citext extension

Revision ID: 68472b20cd10
Revises: 4b7e95952d72
Create Date: 2025-11-14 07:56:10.138387

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '68472b20cd10'
down_revision: Union[str, Sequence[str], None] = '4b7e95952d72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS citext;")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP EXTENSION IF EXISTS citext;")
