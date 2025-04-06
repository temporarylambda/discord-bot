"""Database Init

Revision ID: 134a29cc5e5e
Revises: 
Create Date: 2025-04-06 12:45:02.269174

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = '134a29cc5e5e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'daily_check_in_topics',
        sa.Column('id', mysql.INTEGER(unsigned=True), nullable=False),
        sa.Column('user_id', mysql.INTEGER(unsigned=True), nullable=True),
        sa.Column('topic_id', mysql.INTEGER(unsigned=True), nullable=True),
        sa.Column('status', sa.String(255), nullable=True),
        sa.Column('user_inventory_id', mysql.INTEGER(unsigned=True), nullable=True),
        sa.Column('skipped_at', sa.TIMESTAMP, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('discord_id', 'user_id'),
        sa.Index('topic_id', 'topic_id'),
        sa.Index('status', 'status'),
        sa.Index('user_inventory_id', 'user_inventory_id')
    )

    # merchandises 表格
    op.create_table(
        'merchandises',
        sa.Column('id', mysql.INTEGER(unsigned=True), nullable=False),
        sa.Column('user_id', mysql.INTEGER(unsigned=True), nullable=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('price', mysql.INTEGER(unsigned=True), nullable=False, default=0),
        sa.Column('system_type', sa.String(255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('deleted_at', sa.TIMESTAMP, nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('user_id', 'user_id')
    )

    # topics 表格
    op.create_table(
        'topics',
        sa.Column('id', mysql.INTEGER(unsigned=True), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('reward', mysql.INTEGER, nullable=True),
        sa.Column('note', sa.Text, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('deleted_at', sa.TIMESTAMP, nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # transfer_reasons 表格
    op.create_table(
        'transfer_reasons',
        sa.Column('id', mysql.INTEGER(unsigned=True), nullable=False),
        sa.Column('type', sa.String(255), nullable=True),
        sa.Column('reason', sa.String(255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('type', 'type')
    )

    # transfer_records 表格
    op.create_table(
        'transfer_records',
        sa.Column('id', mysql.INTEGER(unsigned=True), nullable=False),
        sa.Column('transfer_reason_id', mysql.INTEGER, nullable=True),
        sa.Column('user_id', mysql.INTEGER(unsigned=True), nullable=True),
        sa.Column('amount', mysql.INTEGER, nullable=False, default=0),
        sa.Column('note', sa.String(255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('reason_id', 'transfer_reason_id'),
        sa.Index('user_id', 'user_id')
    )

    # transfer_relations 表格
    op.create_table(
        'transfer_relations',
        sa.Column('id', mysql.INTEGER(unsigned=True), nullable=False),
        sa.Column('transfer_reason_id', mysql.INTEGER(unsigned=True), nullable=True),
        sa.Column('relation_type', sa.String(255), nullable=True),
        sa.Column('relation_id', mysql.INTEGER(unsigned=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # user_inventories 表格
    op.create_table(
        'user_inventories',
        sa.Column('id', mysql.INTEGER(unsigned=True), nullable=False),
        sa.Column('user_id', mysql.INTEGER(unsigned=True), nullable=True),
        sa.Column('merchandise_id', mysql.INTEGER(unsigned=True), nullable=True),
        sa.Column('status', sa.String(255), nullable=True),
        sa.Column('redeemed_at', sa.TIMESTAMP, nullable=True),
        sa.Column('refunded_at', sa.TIMESTAMP, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('user_id', 'user_id'),
        sa.Index('merchandise_id', 'merchandise_id'),
        sa.Index('status', 'status')
    )

    # users 表格
    op.create_table(
        'users',
        sa.Column('id', mysql.INTEGER(unsigned=True), nullable=False),
        sa.Column('uuid', sa.String(255), nullable=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('balance', sa.BigInteger, nullable=True),
        sa.Column('consecutive_checkin_days', mysql.INTEGER(unsigned=True), nullable=False, default=0),
        sa.Column('latest_checkin_at', sa.TIMESTAMP, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid', name='uuid')
    )

    # 插入預設資料
    op.execute(
        f"""
            INSERT INTO `merchandises` (`id`, `user_id`, `name`, `description`, `price`, `system_type`, `created_at`, `updated_at`, `deleted_at`)
            VALUES
	        (1,NULL,'任務刷新卷','太羞恥的任務？\n不想嘗試的事情？\n就用萬能的任務刷新卷逃過一劫吧！',100,'SYSTEM_CHECK_IN_REFRESH','2025-04-02 23:04:08','2025-04-02 23:04:26',NULL)
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('daily_check_in_topics')
    op.drop_table('merchandises')
    op.drop_table('topics')
    op.drop_table('transfer_reasons')
    op.drop_table('transfer_records')
    op.drop_table('transfer_relations')
    op.drop_table('user_inventories')
    op.drop_table('users')
