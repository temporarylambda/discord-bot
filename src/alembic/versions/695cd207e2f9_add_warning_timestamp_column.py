"""add_warning_timestamp_column

Revision ID: 695cd207e2f9
Revises: fd0e7487593c
Create Date: 2025-06-14 05:58:08.860361

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '695cd207e2f9'
down_revision: Union[str, None] = 'fd0e7487593c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        ALTER TABLE users
        ADD COLUMN checkin_inactive_warned_at TIMESTAMP NULL
        AFTER latest_checkin_at
        """
    )



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'checkin_inactive_warned_at')
