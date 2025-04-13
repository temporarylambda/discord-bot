"""Gambling Eighteen Dices

Revision ID: 9ca5491d4e0c
Revises: 134a29cc5e5e
Create Date: 2025-04-09 13:57:41.642767

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = '9ca5491d4e0c'
down_revision: Union[str, None] = '134a29cc5e5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create gambling table
    op.create_table(
        'gambling',
        sa.Column('id', mysql.INTEGER(unsigned=True), nullable=False),
        sa.Column('user_id', mysql.INTEGER, nullable=True, comment='賭局主持人'),
        sa.Column('status', sa.String(255), nullable=True, default='PENDING', comment='賭局狀態'),
        sa.Column('type', sa.String(255), nullable=True, comment='賭局類型'),
        sa.Column('min_bet', mysql.INTEGER(unsigned=True), nullable=True, comment='最低賭金(小盲注)'),
        sa.Column('max_bet', mysql.INTEGER(unsigned=True), nullable=True, comment='最大賭金(大盲注)'),
        sa.Column('canceled_at', sa.TIMESTAMP, nullable=True, default=None, comment='賭局取消時間'),
        sa.Column('finished_at', sa.TIMESTAMP, nullable=True, default=None, comment='賭局結束時間'),
        sa.Column('created_at', sa.TIMESTAMP, nullable=True, default=sa.func.current_timestamp(), comment='賭局建立時間'),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=True, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('user_id', 'user_id'),
        sa.Index('status', 'status'),
        sa.Index('type', 'type')
    )

        # Create gamblers table
    op.create_table(
        'gamblers',
        sa.Column('id', mysql.INTEGER(unsigned=True), nullable=False),
        sa.Column('gambling_id', mysql.INTEGER(unsigned=True), nullable=True),
        sa.Column('user_id', mysql.INTEGER(unsigned=True), nullable=True, comment='參與者編號'),
        sa.Column('total_bets', mysql.INTEGER(unsigned=True), nullable=True, comment='總下注金額'),
        sa.Column('status', sa.String(255), nullable=True, comment='PENDING: 等候開始, GAMBLING: 賭局中, LOSER: 輸家, WINNER: 贏家, ABSTAIN: 棄權者(等同輸家)'),
        sa.Column('created_at', sa.TIMESTAMP, nullable=True, default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=True, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('gambling_id', 'user_id'),
        sa.Index('gambling_id_2', 'gambling_id'),
        sa.Index('status', 'status')
    )

    # Create gambling_dices_eighteen table
    op.create_table(
        'gambling_dices_eighteen',
        sa.Column('id', mysql.INTEGER(unsigned=True), nullable=False),
        sa.Column('gambling_id', mysql.INTEGER(unsigned=True), nullable=True),
        sa.Column('user_id', mysql.INTEGER(unsigned=True), nullable=True),
        sa.Column('dices', mysql.INTEGER, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=True, default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=True, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('gambling_id', 'user_id'),
        sa.Index('gambling_id_2', 'gambling_id')
    )




def downgrade() -> None:
    """Downgrade schema."""
    # Drop gamblers table
    op.drop_table('gamblers')

    # Drop gambling table
    op.drop_table('gambling')

    # Drop gambling_dices_eighteen table
    op.drop_table('gambling_dices_eighteen')