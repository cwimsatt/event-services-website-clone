"""Fix theme colors relationship

Revision ID: 09b778cc3434
Revises: 76655e9680a0
Create Date: 2024-12-11 01:30:52.380776

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '09b778cc3434'
down_revision = '76655e9680a0'
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
