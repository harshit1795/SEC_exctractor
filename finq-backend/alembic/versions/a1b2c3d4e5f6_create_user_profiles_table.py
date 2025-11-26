"""create_user_profiles_table

Revision ID: a1b2c3d4e5f6
Revises: 14f55112414b
Create Date: 2025-11-26 04:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '14f55112414b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=True),
        sa.Column('firebase_display_name', sa.String(), nullable=True),
        sa.Column('profile_picture_url', sa.String(), nullable=True),
        sa.Column('firebase_photo_url', sa.String(), nullable=True),
        sa.Column('use_alias_as_display', sa.Boolean(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_user_profiles_user_id'), 'user_profiles', ['user_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_profiles_user_id'), table_name='user_profiles')
    op.drop_table('user_profiles')

