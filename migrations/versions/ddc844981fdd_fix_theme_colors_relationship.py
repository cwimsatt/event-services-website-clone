"""Fix theme colors relationship

Revision ID: ddc844981fdd
Revises: d9eacc32a0c7
Create Date: 2024-12-10 16:46:45.104464

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ddc844981fdd'
down_revision = 'd9eacc32a0c7'
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
