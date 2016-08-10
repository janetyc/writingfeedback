from flask import Blueprint, Flask, request, render_template, redirect, url_for, jsonify
from crowdtask.dbquery import DBQuery
from enum import TaskType, RelationType, Status

api = Blueprint('api', __name__, template_folder='templates')

@api.route('/api/add_topic', methods=('GET','POST'))
def add_topic():
    article_id = request.args.get('article_id')
    worker_id = request.args.get('worker_id', u'tester')
    paragraph_topic = request.args.get('paragraph_topic')
    verified_string = request.args.get('verified_string')

    assignment_id = request.args.get('assignment_id')
    hit_id = request.args.get('hit_id')

    #print "add topic ---"
    #print created_user
    #print assignmentId
    #print hitId
    #print "---"

    paragraph_topic_map={}
    problem = ""
    topic_list = []
    if paragraph_topic:
        for item in paragraph_topic.split("|"):
            p_topic = item.split(":")
            if p_topic[0] not in paragraph_topic_map:
                paragraph_topic_map[p_topic[0]] = []

            paragraph_topic_map[p_topic[0]].extend([p_topic[1]])

        for paragraph_idx in paragraph_topic_map:
            topic_sentence_ids = ",".join(paragraph_topic_map[paragraph_idx])
            problem = "%s|%s,%s" % (problem, article_id, paragraph_idx)

            topic_id = DBQuery().add_topic(worker_id, article_id, paragraph_idx, topic_sentence_ids)
            topic_list.append(str(topic_id))

        problem = problem[1:]

    #add task
    DBQuery().add_task(created_user=worker_id, task_type=TaskType.TOPIC, problem=problem, 
                        answer="|".join(topic_list), verified_string=verified_string, 
                        status=Status.WORKING, assignmentId=assignment_id, hitId=hit_id)
    return jsonify(success=1, data=topic_list)

# require implement
@api.route('/api/add_relevance', methods=('GET','POST'))
def add_relevance():
    worker_id = request.args.get('worker_id', u'tester')
    article_id = request.args.get('article_id')
    paragraph_relevance = request.args.get('paragraph_relevance')
    paragraph_topic = request.args.get('paragraph_topic')
    verified_string = request.args.get('verified_string')

    assignment_id = request.args.get('assignment_id')
    hit_id = request.args.get('hit_id')

    topic_map = {}
    for item in paragraph_topic.split("|"):
        p_topic = item.split(":")
        paragraph_idx = p_topic[0]
        topic_ids = p_topic[1]

        topic_map[paragraph_idx] = topic_ids

    relevance_list = []
    relevance_map = {}

    problem = ""
    if paragraph_relevance:
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
            problem = "%s|%s|%s" % (problem, article_id, paragraph_idx) #should unify

            relevance_id = DBQuery().add_relevance(worker_id, int(article_id), int(paragraph_idx), topic_ids, relevance_ids_str)
            relevance_list.append(str(relevance_id))

        problem = problem[1:]
    else:
        problem = "%s|%s" % (article_id, paragraph_idx) #should unify
        relevance_ids_str = ""
        relevance_id = DBQuery().add_relevance(worker_id, int(article_id), int(paragraph_idx), topic_ids, relevance_ids_str)
        relevance_list.append(str(relevance_id))

    DBQuery().add_task(created_user=worker_id, task_type=TaskType.RELEVANCE, problem=problem, 
                        answer="|".join(relevance_list), verified_string=verified_string, status=Status.WORKING, 
                        assignmentId=assignment_id, hitId=hit_id)

    return jsonify(success=1, data=relevance_list)


@api.route('/api/add_relation', methods=('GET', 'POST'))
def add_relation():
    worker_id = request.args.get('worker_id', u'tester')
    article_id = request.args.get('article_id')
    paragraph_relation = request.args.get('paragraph_relation')
    verified_string = request.args.get('verified_string')

    assignment_id = request.args.get('assignment_id')
    hit_id = request.args.get('hit_id')

    problem = ""
    relation_list = []
    for item in paragraph_relation.split("|"):
        p_relation = item.split(":")
        paragraph_idx = p_relation[0]
        pair_ids = p_relation[1]
        relation_type = p_relation[2]

        #should unify
        problem = "%s|%s|%s" % (problem, article_id, paragraph_idx)

        relation_id = DBQuery().add_relation(worker_id, int(article_id), int(paragraph_idx), pair_ids, relation_type, "")
        relation_list.append(str(relation_id))

    problem = problem[1:]


    DBQuery().add_task(created_user=worker_id, task_type=TaskType.RELATION, problem=problem,
                        answer="|".join(relation_list), verified_string=verified_string,
                        status=Status.WORKING, assignmentId=assignment_id, hitId=hit_id)

    return jsonify(success=1, data=relation_list)

@api.route('/api/add_link', methods=('GET', 'POST'))
def add_link():
    worker_id = request.args.get('worker_id', u'tester')
    article_id = request.args.get('article_id')

    thesis_statement_idx = request.args.get('thesis_statement_idx')
    topic_sentence_ids = request.args.get('topic_sentence_ids')
    thesis_statement_relevance_ids = request.args.get('thesis_statement_relevance_ids')
    topic_sentence_relevance_ids = request.args.get('topic_sentence_relevance_ids')
    common_idea = request.args.get('common_idea')
    rating = request.args.get('rating')
    irrelevance_check = request.args.get('irrelevance_check')
    verified_string = request.args.get('verified_string')

    assignment_id = request.args.get('assignment_id')
    hit_id = request.args.get('hit_id')

    problem = ""
    link_list = []

    ts_list = topic_sentence_ids.split('|')
    tss_ideas_list = thesis_statement_relevance_ids.split('|')
    ts_ideas_list = topic_sentence_relevance_ids.split('|')
    common_idea_list = common_idea.split('|')
    rating_list = rating.split('|')
    irrelevance_check_list = irrelevance_check.split('|')
    print ts_list
    print tss_ideas_list
    print ts_ideas_list
    print common_idea_list
    print rating_list
    print irrelevance_check_list

    for i in range(len(tss_ideas_list)):
        link_id = DBQuery().add_link(worker_id, int(article_id), thesis_statement_idx,
                                     ts_list[i], tss_ideas_list[i], ts_ideas_list[i],
                                     common_idea_list[i], rating_list[i], int(irrelevance_check_list[i]))
        link_list.append(str(link_id))

    problem = "|".join([ "%s,%s,%s" % (article_id, thesis_statement_idx, ts_idx) for ts_idx in ts_list ])
    DBQuery().add_task(created_user=worker_id, task_type=TaskType.LINK, problem=problem,
                        answer="|".join(link_list), verified_string=verified_string,
                        status=Status.WORKING, assignmentId=assignment_id, hitId=hit_id)

    return jsonify(success=1, data=link_list)
