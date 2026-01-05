"""Add passphrase usage tracking

Revision ID: 002
Revises: 001
Create Date: 2025-01-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create passphrase_usage table
    op.create_table(
        'passphrase_usage',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('passphrase', sa.String(), nullable=False),
        sa.Column('repo_id', sa.String(), nullable=True),
        sa.Column('questions_asked', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['repo_id'], ['repositories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on passphrase for faster lookups
    op.create_index('ix_passphrase_usage_passphrase', 'passphrase_usage', ['passphrase'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_passphrase_usage_passphrase', table_name='passphrase_usage')
    op.drop_table('passphrase_usage')

