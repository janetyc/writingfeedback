from datetime import datetime
from crowdtask import db

class Article(db.Model):
    __tablename__ = 'article'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text())
    content = db.Column(db.Text())
    created_time = db.Column(db.DateTime())
    #authors = db.Column(db.Text())
    #keywords = db.Column(db.Text())
    #source = db.Column(db.Text())
    #year = db.Column(db.Integer)

    #def __init__(self, title, content, authors="", keywords="", source="", year=-1):
    #    self.title = title
    #    self.content = content
    #    self.authors = authors
    #    self.keywords = keywords
    #    self.source = source
    #    self.year = year

    def __init__(self, title, content):
        self.title = title
        self.content = content
        self.created_time = datetime.utcnow()

    def __repr__(self):
        return '<Article %r>' % self.title

class Paragraph(db.Model):
    __tablename__ = 'paragraph'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.Integer)
    paragraph_idx = db.Column(db.Integer) # index of paragraph in the article
    content = db.Column(db.Text())
    created_time = db.Column(db.DateTime())

    def __init__(self, article_id, paragraph_idx, content):
        self.article_id = article_id
        self.paragraph_idx = paragraph_idx
        self.content = content
        self.created_time = datetime.utcnow()

    def __repr__(self):
        return '<Paragraph %r>' % self.id


class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_user = db.Column(db.Text())
    task_type = db.Column(db.Text())
    problem = db.Column(db.Text()) #article_id|paragraph_idx
    answer = db.Column(db.Text()) #list of output_ids (e.g. relation_id, topic_id, relevance_id)
    verified_string = db.Column(db.Text())
    status = db.Column(db.Integer)
    created_time = db.Column(db.DateTime())
    submited_time = db.Column(db.DateTime())

    hitId = db.Column(db.Text())
    assignmentId = db.Column(db.Text())

    
    def __init__(self, created_user, task_type, problem, answer, verified_string, status, assignmentId, hitId):
        self.created_user = created_user
        self.task_type = task_type
        self.problem = problem
        self.answer = answer
        self.verified_string = verified_string
        self.status = status
        self.created_time = datetime.utcnow()
        self.submited_time = datetime.utcnow()
        self.assignmentId = assignmentId
        self.hitId = hitId

    def __repr__(self):
        return '<Task %r>' % self.created_user


class Topic(db.Model):
    __tablename__ = 'topic'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_user = db.Column(db.Text())
    article_id = db.Column(db.Integer)
    paragraph_idx = db.Column(db.Integer)
    topic_sentence_ids = db.Column(db.Text())
    created_time = db.Column(db.DateTime())

    def __init__(self, created_user, article_id, paragraph_idx, topic_sentence_ids):
        self.created_user = created_user
        self.article_id = article_id
        self.paragraph_idx = paragraph_idx
        self.topic_sentence_ids = topic_sentence_ids
        self.created_time = datetime.utcnow()

    def __repr__(self):
        return '<Topic %r>' % self.created_user


class Relation(db.Model):
    __tablename__ = 'relation'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_user = db.Column(db.Text())
    article_id = db.Column(db.Integer)
    paragraph_idx = db.Column(db.Integer)
    sentence_pair = db.Column(db.Text()) #two neighboring sentences
    relation_type = db.Column(db.Text())
    others = db.Column(db.Text())
    created_time = db.Column(db.DateTime())

    def __init__(self, created_user, article_id, paragraph_idx, sentence_pair, relation_type, others):
        self.created_user = created_user
        self.article_id = article_id
        self.paragraph_idx = paragraph_idx
        self.sentence_pair = sentence_pair
        self.relation_type = relation_type
        self.others = others
        self.created_time = datetime.utcnow()

    def __repr__(self):
        return '<Relation %r>' % self.created_user

'''
    Relevance for each paragraph
    - topic_sentence: sentence1, sentence2
    - relevance_ids: word_idx1,word_idx2,word_idx3
'''
class Relevance(db.Model):
    __tablename__ = 'relevance'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_user = db.Column(db.Text())
    article_id = db.Column(db.Integer)
    paragraph_idx = db.Column(db.Integer)
    topic_sentence_idx = db.Column(db.Text())
    relevance_ids = db.Column(db.Text())
    created_time = db.Column(db.DateTime())

    def __init__(self, created_user, article_id, paragraph_idx, topic_sentence_idx, relevance_ids):
        self.created_user = created_user
        self.article_id = article_id
        self.paragraph_idx = paragraph_idx
        self.topic_sentence_idx = topic_sentence_idx
        self.relevance_ids = relevance_ids
        self.created_time = datetime.utcnow()

    def __repr__(self):
        return '<Relevance %r>' % self.created_user


''' Store the structure of a paragraph (aggregate results from accepted task)
    - topic: #sentence_2,sentence_3
    - relevance: sentence_2:relevance_1,relevance_2|sentence_1:relevance_1
    - relation: sentence_1,sentence_2:relation_type
    - others: worker_defined
    - task_history: task_id1,task_id2,task_id3
'''
class Structure(db.Model):
    __tablename__ = 'structure'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.Integer)
    paragraph_idx = db.Column(db.Integer)
    topic = db.Column(db.Text())
    relevance = db.Column(db.Text())
    relation = db.Column(db.Text())
    others = db.Column(db.Text())
    task_history = db.Column(db.Text())

    def __init__(self, article_id, paragraph_idx, topic, relevance, relation, others, task_history):
        self.article_id = article_id
        self.paragraph_idx = paragraph_idx
        self.topic = topic
        self.relevance = relevance
        self.relation = relation
        self.others = others
        self.task_history = task_history

    def __repr__(self):
        return '<Structure %r>' % self.article_id
