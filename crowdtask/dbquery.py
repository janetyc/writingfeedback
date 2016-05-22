from crowdtask.models import Task, Article, Paragraph, Topic, Relation, Relevance
from crowdtask.models import Workflow, Structure
from crowdtask import db
from enum import TaskType

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
    def add_task(self, created_user, task_type, problem, answer, 
                 verified_string, status, assignmentId, hitId):

        task = Task(created_user, task_type, problem, answer, 
                    verified_string, status, assignmentId, hitId)
        db.session.add(task)
        db.session.commit()
        return task.id

    def add_topic(self, created_user, article_id, paragraph_id, topic_sentence_ids):
        topic = Topic(created_user, article_id, paragraph_id, topic_sentence_ids)
        db.session.add(topic)
        db.session.commit()

        return topic.id

    def add_relation(self, created_user, article_id, paragraph_idx, 
                     sentence_pair, relation_type, others):
        relation = Relation(created_user, article_id, paragraph_idx, 
                            sentence_pair, relation_type, others)
        db.session.add(relation)
        db.session.commit()

        return relation.id

    def add_relevance(self, created_user, article_id, paragraph_idx, 
                      topic_sentence_idx, relevance_ids):
        relevance = Relevance(created_user, article_id, paragraph_idx, 
                              topic_sentence_idx, relevance_ids)
        db.session.add(relevance)
        db.session.commit()

        return relevance.id

    def add_workflow(self, workflow_type):
        workflow = Workflow(workflow_type)
        db.session.add(workflow)
        db.session.commit()

        return workflow.id

    def add_hit_id_to_workflow(self, workflow_id, task_type, hit_id):
        workflow = self.get_workflow_by_id(workflow_id)
        if workflow is None:
            return None

        hit_ids = []
        updated_workflow = Workflow.query.filter_by(id=workflow_id)
        if task_type == TaskType.TOPIC:
            if workflow.topic_hit_ids != "":
                hit_ids = workflow.topic_hit_ids.split(',')

            hit_ids.append(hit_id)
            updated_workflow.update({"topic_hit_ids": ",".join(hit_ids)})
        elif task_type == TaskType.RELEVANCE:
            if workflow.relevance_hit_ids != "":
                hit_ids = workflow.relevance_hit_ids.split(',')
            
            hit_ids.append(hit_id)
            updated_workflow.update({"relevance_hit_ids": ",".join(hit_ids)})
        elif task_type == TaskType.RELATION:
            if workflow.relation_hit_ids !="":
                hit_ids = workflow.relation_hit_ids.split(',')

            hit_ids.append(hit_id)
            updated_workflow.update({"relation_hit_ids": ",".join(hit_ids)})

        db.session.commit()

        return updated_workflow

    #update status
    def update_task_status_by_worker_assignment_id(self, workerId, assignmentId, status):
        task = Task.query.filter_by(assignmentId=assignmentId, 
                                    created_user=workerId).update({"status": status})
        db.session.commit()

        return task

    #get data from database
    def get_workflow_by_id(self, workflow_id):
        workflow = Workflow.query.filter_by(id=workflow_id).first()
        return workflow

    def get_task_by_id(self, task_id):
        task = Task.query.filter_by(id=task_id).first()
        return task

    def get_task_by_worker_assignment_id(self, workerId ,assignmentId):
        task = Task.query.filter_by(assignmentId=assignmentId, created_user=workerId).first()
        return task

    def get_article_by_id(self, article_id):
        article = Article.query.filter_by(id=article_id).first()
        return article

    def get_article_by_title(self, title):
        article = Article.query.filter_by(title=title).first()
        return article

    def get_paragraph_by_id(self, paragraph_id):
        paragraph = Paragraph.query.filter_by(id=paragraph_id).first()
        return paragraph

    def get_topics_by_article_paragraph_id(self, article_id, paragraph_idx):
        topics = Topic.query.filter_by(article_id=article_id, paragraph_idx=paragraph_idx)
        return topics

    def get_topics_by_article_id(self, article_id):
        topics = Topic.query.filter_by(article_id=article_id)
        return topics

    def get_topics_by_hit_id(self, hit_id):
        tasks = Task.query.filter_by(hit_id=hit_id)
        for task in tasks:
            answer_list = task.answer.split("|")

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
