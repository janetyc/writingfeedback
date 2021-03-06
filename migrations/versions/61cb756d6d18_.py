"""empty message

Revision ID: 61cb756d6d18
Revises: a2b4b3057c2c
Create Date: 2016-05-17 19:12:31.179299

"""

# revision identifiers, used by Alembic.
revision = '61cb756d6d18'
down_revision = 'a2b4b3057c2c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('assignmentId', sa.Text(), nullable=True))
    op.add_column('task', sa.Column('hitId', sa.Text(), nullable=True))
    op.drop_column('task', 'assignment_id')
    op.drop_column('task', 'hit_id')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('task', sa.Column('hit_id', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('task', sa.Column('assignment_id', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_column('task', 'hitId')
    op.drop_column('task', 'assignmentId')
    ### end Alembic commands ###
