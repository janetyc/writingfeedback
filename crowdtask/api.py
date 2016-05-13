import random
import string
from flask import Blueprint, Flask, request, render_template, redirect, url_for, jsonify
from crowdtask.dbquery import DBQuery
from enum import TaskType, RelationType, Status

api = Blueprint('api', __name__, template_folder='templates')


@api.route('/api/add_topic', methods=('GET','POST'))
def add_topic():
    article_id = request.args.get('article_id')
    created_user = request.args.get('created_user', u'tester')
    paragraph_topic = request.args.get('paragraph_topic')

    paragraph_topic_map={}

    for item in paragraph_topic.split("|"):
        p_topic = item.split(":")
        if p_topic[0] not in paragraph_topic_map:
            paragraph_topic_map[p_topic[0]] = []

        paragraph_topic_map[p_topic[0]].extend([p_topic[1]])

    topic_list = []
    problem = ""
    for paragraph_idx in paragraph_topic_map:
        topic_sentence_ids = ",".join(paragraph_topic_map[paragraph_idx])
        problem = "%s|%s|%s" % (problem, article_id, paragraph_idx)

        topic_id = DBQuery().add_topic(created_user, article_id, paragraph_idx, topic_sentence_ids)
        topic_list.append(str(topic_id))

    verified_string = generate_verified_str(6)
    DBQuery().add_task(created_user, TaskType.TOPIC, problem, "|".join(topic_list), verified_string, Status.REVIEW)

    return jsonify(success=1, data=topic_list)

# require implement
@api.route('/api/add_relevance', methods=('GET','POST'))
def add_relevance():
    created_user = request.args.get('created_user', u'tester')
    article_id = request.args.get('article_id')
    paragraph_relevance = request.args.get('paragraph_relevance')
    paragraph_topic = request.args.get('paragraph_topic')
    #print "relevance: %s" % paragraph_relevance
    #print "topic: %s" % paragraph_topic

    topic_map = {}
    for item in paragraph_topic.split("|"):
        p_topic = item.split(":")
        paragraph_idx = p_topic[0]
        topic_ids = p_topic[1]

        topic_map[paragraph_idx] = topic_ids

    relevance_list = []
    relevance_map = {}
    for item in paragraph_relevance.split("|"):
        p_relevance = item.split(":")
        paragraph_idx = p_relevance[0]
        relevance_ids = p_relevance[1]

        if paragraph_idx not in relevance_map:
            relevance_map[paragraph_idx] = []

        relevance_map[paragraph_idx].extend([relevance_ids])

    problem = ""
    for paragraph_idx in relevance_map:
        topic_ids = ""
        if paragraph_idx in topic_map:
            topic_ids = topic_map[paragraph_idx]

        relevance_ids_str = ",".join(relevance_map[paragraph_idx])
        problem = "%s|%s|%s" % (problem, article_id, paragraph_idx)

        relevance_id = DBQuery().add_relevance(created_user, int(article_id), int(paragraph_idx), topic_ids, relevance_ids_str)
        relevance_list.append(str(relevance_id))

    verified_string = generate_verified_str(6)
    DBQuery().add_task(created_user, TaskType.RELEVANCE, problem, "|".join(relevance_list), verified_string, Status.REVIEW)

    return jsonify(success=1, data=relevance_list)

# require implement
@api.route('/api/add_relation', methods=('GET','POST'))
def add_relation():
    created_user = request.args.get('created_user', u'tester')
    article_id = request.args.get('article_id')
    paragraph_relation = request.args.get('paragraph_relation')

    problem = ""
    relation_list = []
    for item in paragraph_relation.split("|"):
        p_relation = item.split(":")
        paragraph_idx = p_relation[0]
        pair_ids = p_relation[1]
        relation_type = p_relation[2]

        problem = "%s|%s|%s" % (problem, article_id, paragraph_idx)

        relation_id = DBQuery().add_relation(created_user, int(article_id), int(paragraph_idx), pair_ids, relation_type, "")
        relation_list.append(str(relation_id))

    verified_string = generate_verified_str(6)
    DBQuery().add_task(created_user, TaskType.RELATION, problem, "|".join(relation_list), verified_string, Status.REVIEW)

    return jsonify(success=1, data=relation_list)


def generate_verified_str(number):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(number))
