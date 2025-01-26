"""Added image_url column

Revision ID: 4f1e0e11661f
Revises: 46bd99b65f9a
Create Date: 2025-01-26 12:05:10.678032

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f1e0e11661f'
down_revision = '46bd99b65f9a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('movie', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_url', sa.String(length=500), nullable=True))
        batch_op.drop_column('image_filename')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('movie', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_filename', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
        batch_op.drop_column('image_url')

    # ### end Alembic commands ###
