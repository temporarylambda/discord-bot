"""unactive_related_column_add

Revision ID: e16eff5d1b50
Revises: 695cd207e2f9
Create Date: 2025-06-18 10:56:57.093754

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e16eff5d1b50'
down_revision: Union[str, None] = '695cd207e2f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE users
        ADD COLUMN deleted_at TIMESTAMP NULL
        AFTER updated_at
        """
    )
    op.execute(
        """
        ALTER TABLE users
        ADD COLUMN latest_message_at TIMESTAMP NULL
        AFTER latest_checkin_at
        """
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'deleted_at')
    op.drop_column('users', 'latest_message_at')
    pass
