from crowdtask import db

class Article(db.Model):
    __tablename__ = 'article'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(80))
    content = db.Column(db.String(500))
    #authors = db.Column(db.String(150))
    #keywords = db.Column(db.String(80))
    #source = db.Column(db.String(80))
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

    def __repr__(self):
        return '<Article %r>' % self.title

class Paragraph(db.Model):
    __tablename__ = 'paragraph'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    article_id = db.Column(db.Integer)
    paragraph_idx = db.Column(db.Integer) # index of paragraph in the article
    content = db.Column(db.String(200))

    def __init__(self, article_id, paragraph_idx, content):
        self.article_id = article_id
        self.paragraph_idx = paragraph_idx
        self.content = content

    def __repr__(self):
        return '<Paragraph %r>' % self.id


class Task(db.Model):
    __tablename__ = 'task'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_type = db.Column(db.String(80))
    created_user = db.Column(db.String(80))
    output = db.Column(db.String(80))

    def __init__(self, created_user, task_type):
        self.created_user = created_user
        self.task_type = task_type

    def __repr__(self):
        return '<Task %r>' % self.created_user


class Topic(db.Model):
    __tablename__ = 'topic'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_user = db.Column(db.String(80))
    article_id = db.Column(db.Integer)
    paragraph_idx = db.Column(db.Integer)
    topic_sentence_ids = db.Column(db.String(100))

    def __init__(self, created_user, article_id, paragraph_idx, topic_sentence_ids):
        self.created_user = created_user
        self.article_id = article_id
        self.paragraph_idx = paragraph_idx
        self.topic_sentence_ids = topic_sentence_ids

    def __repr__(self):
        return '<Topic %r>' % self.created_user


class Relation(db.Model):
    __tablename__ = 'relation'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_user = db.Column(db.String(80))
    article_id = db.Column(db.Integer)
    paragraph_idx = db.Column(db.Integer)
    sentence_pair = db.Column(db.String(120)) #two neighboring sentences
    relation_type = db.Column(db.String(100))
    others = db.Column(db.String(100))

    def __init__(self, created_user, article_id, paragraph_idx, sentence_pair, relation_type, others):
        self.created_user = created_user
        self.article_id = article_id
        self.paragraph_idx = paragraph_idx
        self.sentence_pair = sentence_pair
        self.relation_type = relation_type
        self.others = others

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
    created_user = db.Column(db.String(80))
    article_id = db.Column(db.Integer)
    paragraph_idx = db.Column(db.Integer)
    topic_sentence_idx = db.Column(db.String(100))
    relevance_ids = db.Column(db.String(100))

    def __init__(self, created_user, article_id, paragraph_idx, topic_sentence_idx, relevance_ids):
        self.created_user = created_user
        self.article_id = article_id
        self.paragraph_idx = paragraph_idx
        self.topic_sentence_idx = topic_sentence_idx
        self.relevance_ids = relevance_ids

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
    topic = db.Column(db.String(200))
    relevance = db.Column(db.String(200))
    relation = db.Column(db.String(200))
    others = db.Column(db.String(200))
    task_history = db.Column(db.String(300))

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
