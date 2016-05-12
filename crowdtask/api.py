from flask import Blueprint, Flask, request, render_template, redirect, url_for, jsonify
from crowdtask.dbquery import DBQuery

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
    for paragraph_idx in paragraph_topic_map:
        topic_sentence_ids = ",".join(paragraph_topic_map[paragraph_idx])
        DBQuery().add_topic(created_user, article_id, paragraph_idx, topic_sentence_ids)
        topic_list.append((article_id, paragraph_idx, topic_sentence_ids))

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

    for paragraph_idx in relevance_map:
        topic_ids = ""
        if paragraph_idx in topic_map:
            topic_ids = topic_map[paragraph_idx]


        relevance_ids_str = ",".join(relevance_map[paragraph_idx])
        #print "----- insert db -----"
        #print "paragraph: %s" % paragraph_idx
        #print "relevance: %s" % relevance_ids_str
        #print "topic: %s" % topic_ids
        DBQuery().add_relevance(created_user, int(article_id), int(paragraph_idx), topic_ids, relevance_ids_str)
        relevance_list.append((article_id, paragraph_idx, topic_ids, relevance_ids))

    return jsonify(success=1, data=relevance_list)


# require implement
@api.route('/api/add_relation', methods=('GET','POST'))
def add_relation():
    created_user = request.args.get('created_user', u'tester')
    article_id = request.args.get('article_id')
    paragraph_relation = request.args.get('paragraph_relation')

    relation_list = []
    for item in paragraph_relation.split("|"):
        p_relation = item.split(":")
        paragraph_idx = p_relation[0]
        pair_ids = p_relation[1]
        relation_type = p_relation[2]

        relation_list.append((created_user, int(article_id), int(paragraph_idx), pair_ids, relation_type, ""))
        DBQuery().add_relation(created_user, int(article_id), int(paragraph_idx), pair_ids, relation_type, "")

    #print relation_list

    return jsonify(success=1, data=[])
