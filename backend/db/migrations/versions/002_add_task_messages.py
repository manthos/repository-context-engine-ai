"""add task status and error messages

Revision ID: 002
Revises: 001
Create Date: 2026-01-06 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Add status_message and error_message columns to tasks table
    op.add_column('tasks', sa.Column('status_message', sa.Text(), nullable=True))
    op.add_column('tasks', sa.Column('error_message', sa.Text(), nullable=True))


def downgrade():
    # Remove the columns
    op.drop_column('tasks', 'error_message')
    op.drop_column('tasks', 'status_message')
