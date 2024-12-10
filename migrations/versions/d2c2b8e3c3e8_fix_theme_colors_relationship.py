"""Fix theme colors relationship

Revision ID: d2c2b8e3c3e8
Revises: e22d6a180b12
Create Date: 2024-12-10 15:56:42.718623

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2c2b8e3c3e8'
down_revision = 'e22d6a180b12'
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
