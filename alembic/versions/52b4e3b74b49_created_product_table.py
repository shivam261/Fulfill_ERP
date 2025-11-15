"""created product table 

Revision ID: 52b4e3b74b49
Revises: 68472b20cd10
Create Date: 2025-11-14 08:28:16.586608

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '52b4e3b74b49'
down_revision: Union[str, Sequence[str], None] = '68472b20cd10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
