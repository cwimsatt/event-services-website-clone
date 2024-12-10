"""Fix theme colors relationship

Revision ID: 76655e9680a0
Revises: c7a9cee1bfb3
Create Date: 2024-12-10 22:45:47.542788

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76655e9680a0'
down_revision = 'c7a9cee1bfb3'
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
