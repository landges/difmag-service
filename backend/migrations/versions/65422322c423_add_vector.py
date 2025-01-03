"""add vector

Revision ID: 65422322c423
Revises: 70c810d3cbe5
Create Date: 2025-01-03 01:54:30.194194

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector


# revision identifiers, used by Alembic.
revision: str = '65422322c423'
down_revision: Union[str, None] = '70c810d3cbe5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('images', sa.Column('mbedding', pgvector.sqlalchemy.vector.VECTOR(dim=2048), nullable=True))
    op.alter_column('images', 'hash',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('images', 'hash',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_column('images', 'mbedding')
    # ### end Alembic commands ###
