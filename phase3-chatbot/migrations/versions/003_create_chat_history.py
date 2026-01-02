"""Create chat_history table

Revision ID: 003
Revises: 002
Create Date: 2025-12-19

Spec Reference: specs/database/chat-history.md
Tasks: 1.1, 1.2
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Create chat_history table
    op.create_table(
        'chat_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(100), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', JSONB, nullable=True),
        sa.Column('timestamp', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name='check_role')
    )

    # Create indexes for performance
    op.create_index('idx_chat_history_user_id', 'chat_history', ['user_id'])
    op.create_index('idx_chat_history_session_id', 'chat_history', ['session_id'])
    op.create_index('idx_chat_history_timestamp', 'chat_history', ['timestamp'])
    op.create_index(
        'idx_chat_history_lookup',
        'chat_history',
        ['user_id', 'session_id', 'is_deleted', sa.text('timestamp DESC')]
    )


def downgrade():
    op.drop_index('idx_chat_history_lookup', table_name='chat_history')
    op.drop_index('idx_chat_history_timestamp', table_name='chat_history')
    op.drop_index('idx_chat_history_session_id', table_name='chat_history')
    op.drop_index('idx_chat_history_user_id', table_name='chat_history')
    op.drop_table('chat_history')
