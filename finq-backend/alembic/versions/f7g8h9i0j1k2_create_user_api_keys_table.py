"""create_user_api_keys_table

Revision ID: f7g8h9i0j1k2
Revises: a1b2c3d4e5f6
Create Date: 2026-02-03 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7g8h9i0j1k2'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_api_keys table for BYOK (Bring Your Own Key) functionality
    op.create_table(
        'user_api_keys',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('gemini_api_key_encrypted', sa.String(), nullable=True),
        sa.Column('fred_api_key_encrypted', sa.String(), nullable=True),
        sa.Column('gemini_key_last_validated', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fred_key_last_validated', sa.DateTime(timezone=True), nullable=True),
        sa.Column('gemini_key_is_valid', sa.Boolean(), nullable=True),
        sa.Column('fred_key_is_valid', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_user_api_keys_user_id'), 'user_api_keys', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_api_keys_user_id'), table_name='user_api_keys')
    op.drop_table('user_api_keys')
