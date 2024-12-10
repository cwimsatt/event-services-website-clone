"""Fix theme colors relationship

Revision ID: 57e6d432639c
Revises: 7041cafc7849
Create Date: 2024-12-10 22:36:37.580083

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57e6d432639c'
down_revision = '7041cafc7849'
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
