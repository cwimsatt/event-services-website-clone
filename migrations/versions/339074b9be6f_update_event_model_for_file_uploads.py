"""update event model for file uploads

Revision ID: 339074b9be6f
Revises: 21441cf1119c
Create Date: 2024-12-04 23:42:57.286293

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '339074b9be6f'
down_revision = '21441cf1119c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_path', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('video_path', sa.String(length=500), nullable=True))
        batch_op.drop_column('image_url')
        batch_op.drop_column('video_url')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('video_url', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('image_url', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
        batch_op.drop_column('video_path')
        batch_op.drop_column('image_path')

    # ### end Alembic commands ###