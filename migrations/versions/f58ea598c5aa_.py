"""empty message

Revision ID: f58ea598c5aa
Revises: 92148da0a623
Create Date: 2016-10-04 16:00:42.619825

"""

# revision identifiers, used by Alembic.
revision = 'f58ea598c5aa'
down_revision = '92148da0a623'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('peerannotation', 'relation')
    op.drop_column('peerannotation', 'irrelevance')
    op.drop_column('peerannotation', 'others')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('peerannotation', sa.Column('others', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('peerannotation', sa.Column('irrelevance', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('peerannotation', sa.Column('relation', sa.TEXT(), autoincrement=False, nullable=True))
    ### end Alembic commands ###
