from crowdtask.models import Article, Paragraph
from crowdtask.models import Task, Topic, Relation, Relevance, Link
from crowdtask.models import Workflow, Structure, GoldenStructure
from crowdtask.models import PeerAnnotation
from crowdtask import db
from enum import TaskType

class DBQuery(object):
    # ************************************************** #
    #               Add data from database               #
    # ************************************************** #
    # article
    def add_article(self, title, content, authors, source, year):
        article = Article(title, content, authors, source, year)
        db.session.add(article)
        db.session.commit()

        return article.id

    def add_paragraph(self, article_id, paragraph_idx, content):
        paragraph = Paragraph(article_id, paragraph_idx, content)
        db.session.add(paragraph)
        db.session.commit()

        return paragraph.id

    # crowd task
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

    def add_link(self, created_user, article_id, thesis_statement_idx, topic_sentence_idx,
                 thesis_statement_relevance_ids, topic_sentence_relevance_ids, common_idea, rating, irrelevance_check):
        link = Link(created_user, article_id, thesis_statement_idx, topic_sentence_idx,
                    thesis_statement_relevance_ids, topic_sentence_relevance_ids, common_idea, rating, irrelevance_check)

        db.session.add(link)
        db.session.commit()

        return link.id

    def add_peer_annotation(self, created_user, article_id, topic, relevance):
        peer_annotatio = PeerAnnotation(created_user, article_id, topic, relevance)
        db.session.add(peer_annotatio)
        db.session.commit()

    def add_golden_structure(self, created_user, article_id, topic, irrelevance, relevance, relation=None, others=None):
        goldenstructure = GoldenStructure(created_user, article_id, topic, irrelevance, relevance, relation, others)
        db.session.add(goldenstructure)
        db.session.commit()

    # crowd workflow - manage task
    def add_workflow(self, workflow_type, article_id, source=None, server=None):
        workflow = Workflow(workflow_type, article_id, source, server)
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
            if workflow.topic_hit_ids and workflow.topic_hit_ids != "":
                hit_ids = workflow.topic_hit_ids.split(',')

            hit_ids.append(hit_id)
            updated_workflow.update({"topic_hit_ids": ",".join(hit_ids)})
        elif task_type == TaskType.RELEVANCE:
            if workflow.relevance_hit_ids and workflow.relevance_hit_ids != "":
                hit_ids = workflow.relevance_hit_ids.split(',')

            hit_ids.append(hit_id)
            updated_workflow.update({"relevance_hit_ids": ",".join(hit_ids)})
        elif task_type == TaskType.RELATION:
            if workflow.relation_hit_ids and workflow.relation_hit_ids != "":
                hit_ids = workflow.relation_hit_ids.split(',')

            hit_ids.append(hit_id)
            updated_workflow.update({"relation_hit_ids": ",".join(hit_ids)})

        elif task_type == TaskType.LINK:
            if workflow.link_hit_ids and workflow.link_hit_ids != "":
                hit_ids = workflow.link_hit_ids.split(',')

            print workflow.link_hit_ids
            hit_ids.append(hit_id)
            print hit_ids

            updated_workflow.update({"link_hit_ids": ",".join(hit_ids)})

        db.session.commit()

        return updated_workflow

    # ************************************************** #
    #               Update data from database            #
    # ************************************************** #
    # task status
    def update_task_status_by_worker_assignment_id(self, workerId, assignmentId, status):
        task = Task.query.filter_by(assignmentId=assignmentId,
                                    created_user=workerId).update({"status": status})
        db.session.commit()

        return task

    # ************************************************** #
    #               Get data from database               #
    # ************************************************** #
    # workflow
    def get_workflow_by_id(self, workflow_id):
        workflow = Workflow.query.filter_by(id=workflow_id).first()
        return workflow

    def get_workflows_by_article_id(self, article_id):
        workflows = Workflow.query.filter_by(article_id=article_id).all()
        return workflows

    def get_task_by_id(self, task_id):
        task = Task.query.filter_by(id=task_id).first()
        return task

    # task
    def get_task_by_worker_assignment_id(self, workerId, assignmentId):
        task = Task.query.filter_by(assignmentId=assignmentId, created_user=workerId).first()
        return task

    def get_task_by_code(self, code):
        task = Task.query.filter_by(verified_string=code).first()
        return task

    def get_all_tasks(self):
        all_tasks = Task.query.all()
        return all_tasks

    # article
    def get_article_by_id(self, article_id):
        article = Article.query.filter_by(id=article_id).first()
        return article

    def get_article_by_title(self, title):
        article = Article.query.filter_by(title=title).first()
        return article

    def get_article_by_title_and_authors(self, title, authors):
        article = Article.query.filter_by(title=title, authors=authors).first()
        return article

    def get_all_articles(self):
        all_articles = Article.query.all()
        return all_articles

    def get_article_count(self):
        return Article.query.count()

    def get_article_paginate(self, page, per_page):
        articles = Article.query.order_by(Article.created_time.desc()).paginate(page=page, per_page=per_page)
        return articles

    # paragraph
    def get_paragraph_by_id(self, paragraph_id):
        paragraph = Paragraph.query.filter_by(id=paragraph_id).first()
        return paragraph

    def get_paragraphs_by_article_id(self, article_id):
        paragraphs = Paragraph.query.filter_by(article_id=article_id).all()
        return paragraphs

    def get_all_paragraphs(self):
        all_paragraphs = Paragraph.query.all()
        return all_paragraphs

    # topic
    def get_topics_by_article_paragraph_id(self, article_id, paragraph_idx):
        topics = Topic.query.filter_by(article_id=article_id, paragraph_idx=paragraph_idx).all()
        return topics

    def get_topics_by_article_id(self, article_id):
        topics = Topic.query.filter_by(article_id=article_id).all()
        return topics

    def get_topics_by_hit_id(self, hit_id):
        tasks = Task.query.filter_by(hitId=hit_id)

        answers_list = []
        for task in tasks:
            if task.answer == "":
                continue

            topic_ids = task.answer.split("|")

            for topic_id in topic_ids:
                topic_list = self.get_topic_by_id(int(topic_id))
                answers_list.extend(topic_list)

        return answers_list

    def get_topic_by_id(self, topic_id):
        topic_list = []
        topic = Topic.query.filter_by(id=topic_id).first()
        for topic_sentence in topic.topic_sentence_ids.split(","):
            topic_list.append(("%d-%d" % (topic.article_id, topic.paragraph_idx), topic_sentence, topic.created_user))

        return topic_list

    def get_all_topics(self):
        all_topics = Topic.query.all()
        return all_topics

    def get_links_by_hit_id(self, hit_id):
        tasks = Task.query.filter_by(hitId=hit_id)

        answers_list = []
        for task in tasks:
            link_ids = task.answer.split("|")
            for link_id in link_ids:
                link_list = self.get_link_by_id(int(link_id))
                answers_list.extend(link_list)

        return answers_list

    def get_link_by_id(self, link_id):
        link_list = []
        link = Link.query.filter_by(id=link_id).first()
        if not link:
            return []

        if link.topic_sentence_relevance_ids and link.topic_sentence_relevance_ids != "":
            link_list.append((link.article_id, link.thesis_statement_idx, link.topic_sentence_idx,
                              link.thesis_statement_relevance_ids.split(","), link.topic_sentence_relevance_ids.split(","),
                              link.rating, link.irrelevance_check, link.created_user, link.common_idea))

        return link_list

    # relevance
    def get_relevances_by_hit_id(self, hit_id):
        tasks = Task.query.filter_by(hitId=hit_id)

        answers_list = []
        for task in tasks:
            if not task.answer or task.answer == "":
                continue

            relevance_ids = task.answer.split("|")
            for relevance_id in relevance_ids:
                relevance_list = self.get_relevance_by_id(int(relevance_id))
                answers_list.extend(relevance_list)

        return answers_list

    # return relevance: [(article_id, paragraph_idx, relevance_word1, topic_sentence_idx, created_user), ...]
    def get_relevance_by_id(self, relevance_id):
        relevance_list = []
        relevance = Relevance.query.filter_by(id=relevance_id).first()
        if not relevance:
            return []

        topic_sentence_idx = relevance.topic_sentence_idx
        paragraph_idx = relevance.paragraph_idx
        article_id = relevance.article_id
        created_user = relevance.created_user

        if relevance.relevance_ids and relevance.relevance_ids != "":
            for relevance_word in relevance.relevance_ids.split(","):
                relevance_list.append((article_id, paragraph_idx, relevance_word, topic_sentence_idx, created_user))

        return relevance_list

    def get_peer_annotation_by_id(self, peer_annotation_id):
        peer_annotation = PeerAnnotation.query.filter_by(id=int(peer_annotation_id)).first()
        return peer_annotation

    def get_peer_annotations_by_article_id(self, article_id):
        all_peer_annotations = PeerAnnotation.query.filter_by(article_id=article_id).all()
        return all_peer_annotations

    def get_peer_count_by_article_id(self, article_id):
        return PeerAnnotation.query.filter_by(article_id=article_id).count()

    def get_golden_structure_by_id(self, golden_id):
        golden_structure = GoldenStructure.query.filter_by(id=int(golden_id)).first()
        return golden_structure

    def get_golden_structures_by_article_id(self, article_id):
        all_goldenstructures = GoldenStructure.query.filter_by(article_id=article_id).all()
        return all_goldenstructures
    
