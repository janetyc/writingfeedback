"""empty message

Revision ID: 3d9b46af0171
Revises: 0618e7d6c610
Create Date: 2016-05-16 19:35:48.001826

"""

# revision identifiers, used by Alembic.
revision = '3d9b46af0171'
down_revision = '0618e7d6c610'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('article', sa.Column('created_time', sa.DateTime(), nullable=True))
    op.add_column('paragraph', sa.Column('created_time', sa.DateTime(), nullable=True))
    op.add_column('relation', sa.Column('created_time', sa.DateTime(), nullable=True))
    op.add_column('relevance', sa.Column('created_time', sa.DateTime(), nullable=True))
    op.add_column('task', sa.Column('created_time', sa.DateTime(), nullable=True))
    op.add_column('task', sa.Column('submited_time', sa.DateTime(), nullable=True))
    op.add_column('topic', sa.Column('created_time', sa.DateTime(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('topic', 'created_time')
    op.drop_column('task', 'submited_time')
    op.drop_column('task', 'created_time')
    op.drop_column('relevance', 'created_time')
    op.drop_column('relation', 'created_time')
    op.drop_column('paragraph', 'created_time')
    op.drop_column('article', 'created_time')
    ### end Alembic commands ###
