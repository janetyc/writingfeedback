from crowdtask.models import Task, Article, Paragraph, Topic, Relation, Relevance
from crowdtask import create_app, db

class DBQuery(object):

    #insert article
    def add_article(self, title, content):
        article = Article(title, content)
        db.session.add(article)
        db.session.commit()

        return article.id

    def add_paragraph(self, article_id, paragraph_idx, content):
        paragraph = Paragraph(article_id, paragraph_idx, content)
        db.session.add(paragraph)
        db.session.commit()

        return paragraph.id

    #crowd task
    def add_task(self, created_user, article_id, paragraph_idx, pair_ids, relation_type, others):
        task = Task(created_user, article_id, paragraph_idx, pair_ids, relation_type, others)
        db.session.add(task)
        db.session.commit()
        return ""

    def add_topic(self, created_user, article_id, paragraph_id, topic_sentence_ids):
        topic = Topic(created_user, article_id, paragraph_id, topic_sentence_ids)
        db.session.add(topic)
        db.session.commit()

        return topic.id

    def add_relation(self, created_user, article_id, paragraph_idx, sentence_pair, relation_type, others):
        relation = Relation(created_user, article_id, paragraph_idx, sentence_pair, relation_type, others)
        db.session.add(relation)
        db.session.commit()

        return relation.id

    def add_relevance(self, created_user, article_id, paragraph_idx, topic_sentence_idx, relevance_ids):
        relevance = Relevance(created_user, article_id, paragraph_idx, topic_sentence_idx, relevance_ids)
        db.session.add(relevance)
        db.session.commit()

        return relevance.id

    #get data from database
    def get_article_by_id(self, article_id):
        article = Article.query.filter_by(id=article_id).first()
        return article

    def get_article_by_title(self, title):
        article = Article.query.filter_by(title=title).first()
        return article

    def get_paragraph_by_id(self, paragraph_id):
        paragraph = Paragraph.query.filter_by(id=paragraph_id).first()
        return paragraph

    def get_topics_by_paragraph_id(self, paragraph_id):
        return ""

    def get_topics_by_article_id(self, article_id):
        topics = Topic.query.filter_by(article_id=article_id)
        return topics

    def get_paragraphs_by_article_id(self, article_id):
        paragraphs = Paragraph.query.filter_by(article_id=article_id)
        return paragraphs

    def get_all_articles(self):
        all_articles = Article.query.all()

        return all_articles

    def get_all_tasks(self):
        all_tasks = Task.query.all()

        return all_tasks

    def get_all_paragraphs(self):
        all_paragraphs = Paragraph.query.all()

        return all_paragraphs

    def get_all_topics(self):
        all_topics = Topic.query.all()

        return all_topic
