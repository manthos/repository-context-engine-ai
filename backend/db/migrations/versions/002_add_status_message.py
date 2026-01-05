"""Add status_message to tasks table

Revision ID: 002
Revises: 001
Create Date: 2025-01-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Add status_message column to tasks table
    op.add_column('tasks', sa.Column('status_message', sa.Text(), nullable=True))


def downgrade():
    # Remove status_message column from tasks table
    op.drop_column('tasks', 'status_message')

