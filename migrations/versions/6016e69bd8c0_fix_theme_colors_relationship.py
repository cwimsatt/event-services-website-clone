"""Fix theme colors relationship

Revision ID: 6016e69bd8c0
Revises: 3da3f382be0b
Create Date: 2024-12-10 22:04:00.930811

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6016e69bd8c0'
down_revision = '3da3f382be0b'
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