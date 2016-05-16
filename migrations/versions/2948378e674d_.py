"""empty message

Revision ID: 2948378e674d
Revises: None
Create Date: 2016-05-13 09:06:49.878478

"""

# revision identifiers, used by Alembic.
revision = '2948378e674d'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('article',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.Text(), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('paragraph',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('article_id', sa.Integer(), nullable=True),
    sa.Column('paragraph_idx', sa.Integer(), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('relation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_user', sa.Text(), nullable=True),
    sa.Column('article_id', sa.Integer(), nullable=True),
    sa.Column('paragraph_idx', sa.Integer(), nullable=True),
    sa.Column('sentence_pair', sa.Text(), nullable=True),
    sa.Column('relation_type', sa.Text(), nullable=True),
    sa.Column('others', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('relevance',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_user', sa.Text(), nullable=True),
    sa.Column('article_id', sa.Integer(), nullable=True),
    sa.Column('paragraph_idx', sa.Integer(), nullable=True),
    sa.Column('topic_sentence_idx', sa.Text(), nullable=True),
    sa.Column('relevance_ids', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('structure',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('article_id', sa.Integer(), nullable=True),
    sa.Column('paragraph_idx', sa.Integer(), nullable=True),
    sa.Column('topic', sa.Text(), nullable=True),
    sa.Column('relevance', sa.Text(), nullable=True),
    sa.Column('relation', sa.Text(), nullable=True),
    sa.Column('others', sa.Text(), nullable=True),
    sa.Column('task_history', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('task',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_type', sa.Text(), nullable=True),
    sa.Column('created_user', sa.Text(), nullable=True),
    sa.Column('output', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('topic',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_user', sa.Text(), nullable=True),
    sa.Column('article_id', sa.Integer(), nullable=True),
    sa.Column('paragraph_idx', sa.Integer(), nullable=True),
    sa.Column('topic_sentence_ids', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('topic')
    op.drop_table('task')
    op.drop_table('structure')
    op.drop_table('relevance')
    op.drop_table('relation')
    op.drop_table('paragraph')
    op.drop_table('article')
    ### end Alembic commands ###