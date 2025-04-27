"""alertGamblingDicesEighteenTableName

Revision ID: fd0e7487593c
Revises: 9ca5491d4e0c
Create Date: 2025-04-27 11:10:36.558684

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = 'fd0e7487593c'
down_revision: Union[str, None] = '9ca5491d4e0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(
        'gambling_id',
        table_name='gambling_dices_eighteen',
    )

    # 重新建立 gambling_dices_eighteen 賭局骰子資料表的 gambling_id 的 index, 但這次不設 unique
    op.create_index(
        'gambling_dice_unique_id',
        'gambling_dices_eighteen',
        ['gambling_id', 'user_id'],
        unique=False,
    )

    # 新建立一組 index : gambling_id, user_id, dices
    op.create_index(
        'gambling_id_user_id_dices',
        'gambling_dices_eighteen',
        ['gambling_id', 'user_id', 'dices'],
        unique=False,
    )

    # 把 gambling_dices_eighteen.dices 改成 gambling_dices_eighteen.dice
    op.alter_column(
        'gambling_dices_eighteen',
        'dices',
        new_column_name='dice',
        existing_type=mysql.INTEGER,
        existing_nullable=True,
    )

    # 把 gambling_dices_eighteen 改成 gambling_dices
    op.rename_table('gambling_dices_eighteen', 'gambling_dices')
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        'gambling_dice_unique_id',
        table_name='gambling_dices',
    )

    # 重新建立 gambling_dices 賭局骰子資料表的 gambling_id 的 index, 這次設 unique
    op.create_index(
        'gambling_id',
        'gambling_dices',
        ['gambling_id', 'user_id'],
        unique=True,
    )

    # 刪除 gambling_id, user_id, dices 的 index
    op.drop_index(
        'gambling_id_user_id_dices',
        table_name='gambling_dices',
    )

    # 把 gambling_dices.dice 改成 gambling_dices.dices
    op.alter_column(
        'gambling_dices',
        'dice',
        new_column_name='dices',
        existing_type=mysql.INTEGER,
        existing_nullable=True,
    )

    # 把 gambling_dices 改回 gambling_dices_eighteen
    op.rename_table('gambling_dices', 'gambling_dices_eighteen')
    pass
