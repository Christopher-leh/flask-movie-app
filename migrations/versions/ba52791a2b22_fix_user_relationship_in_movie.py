"""Fix User relationship in Movie

Revision ID: ba52791a2b22
Revises: d66b096bbfb8
Create Date: 2025-01-25 20:14:24.616123

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba52791a2b22'
down_revision = 'd66b096bbfb8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('movie', schema=None) as batch_op:
        batch_op.add_column(sa.Column('added_by_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint('movie_added_by_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['added_by_id'], ['id'])
        batch_op.drop_column('added_by')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('movie', schema=None) as batch_op:
        batch_op.add_column(sa.Column('added_by', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('movie_added_by_fkey', 'user', ['added_by'], ['id'])
        batch_op.drop_column('added_by_id')

    # ### end Alembic commands ###
