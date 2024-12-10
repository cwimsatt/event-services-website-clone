"""Fix theme colors relationship

Revision ID: 55630ec4e8e3
Revises: 1525723eee1b
Create Date: 2024-12-10 15:58:28.343007

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55630ec4e8e3'
down_revision = '1525723eee1b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.alter_column('sequence',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=3),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.alter_column('sequence',
               existing_type=sa.Float(precision=3),
               type_=sa.REAL(),
               existing_nullable=True)

    # ### end Alembic commands ###
