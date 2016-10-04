import re
import random
import string
from flask import Blueprint, Flask, request, render_template, redirect, url_for, jsonify
from crowdtask.dbquery import DBQuery

vis_views = Blueprint('vis_views', __name__, template_folder='templates')

# for crowd task
@vis_views.route('/topic_vis', methods=('GET','POST'))
def topic_vis():
    data = {}
    topic_map = {}
    relevance_map = {}
    link_map = {}
    article_ids = []

    if not (request.args.has_key('workflow_id')):
        data = {}
        return render_template('topic_vis.html', data)
    
    workflow_id = request.args.get('workflow_id')
    workflow = DBQuery().get_workflow_by_id(workflow_id)
    
    # topic
    if workflow.topic_hit_ids and workflow.topic_hit_ids != "":
        topic_hits = workflow.topic_hit_ids.split(",")
        for hit_id in topic_hits:
            topic_list_w_worker = DBQuery().get_topics_by_hit_id(hit_id)
            topic_list = [(t[0], t[1]) for t in topic_list_w_worker]

            for par_topic in set(topic_list):
                article_ids.append(par_topic[0].split("-")[0])
                key = "-".join(par_topic)
                topic_map[key] = topic_list.count(par_topic)
    
    # link
    if workflow.link_hit_ids and workflow.link_hit_ids != "":
        link_hits = workflow.link_hit_ids.split(",")
        for hit_id in link_hits:
            link_list_w_worker = DBQuery().get_links_by_hit_id(hit_id)
            for link in link_list_w_worker:
                link_key = "%d-%s,%d-%s" % (link[0],link[1],link[0],link[2])
                if link_key in link_map:
                    link_map[link_key]["thesis_statement_relevance"].extend(link[3])
                    link_map[link_key]["topic_sentence_relevance"].extend(link[4])
                else:
                    link_map[link_key] = {
                        "thesis_statement_relevance":[],
                        "topic_sentence_relevance":[]
                    }
                    link_map[link_key]["thesis_statement_relevance"] = link[3]
                    link_map[link_key]["topic_sentence_relevance"] = link[4]
    #print link_map

    # relevance
    if workflow.relevance_hit_ids and workflow.relevance_hit_ids != "":
        relevance_hits = workflow.relevance_hit_ids.split(",")
        for hit_id in relevance_hits:
            relevance_list_w_worker = DBQuery().get_relevances_by_hit_id(hit_id)
            relevance_list = [(r[0],r[1],r[2],r[3]) for r in relevance_list_w_worker]
            
            for par_relevance in set(relevance_list):
                # paragraph_idx-sentence_idx-word_idx
                
                key = "%d-%d-%s" % (par_relevance[0],par_relevance[1],par_relevance[2])
                relevance_map[key] = relevance_list.count(par_relevance)

    article_ids = set(article_ids)
    if not len(article_ids):
        data = {}
        return render_template('topic_vis.html', data=data)

    article_id = int(article_ids.pop())

    article = DBQuery().get_article_by_id(article_id)
    content_map = {}
    issue_map={}

    topic_tip = 0
    for i, paragraph in enumerate(article.content.split("<BR>")):
        if paragraph:
            sentence_list = re.split(r'(?<=[^A-Z].[.?]) +(?=[A-Z])', paragraph)

            weight_sentence_list = []
            for j, sentence in enumerate(sentence_list):
                topic_key = "%d-%d-%d" % (article_id, i, j)
                sentence = sentence.strip()
                word_list = sentence.split(" ")
                weight_word_list = []
                for k, word in enumerate(word_list):
                    word = word.strip()
                    relevance_key = "%d-%d-%d-%d" % (article_id, i, j, k)
                    if(relevance_key in relevance_map):
                        weight_word_list.append((word, relevance_map[relevance_key]))
                    else:
                        weight_word_list.append((word, 0))

                if(topic_key in topic_map):
                    weight_sentence_list.append((weight_word_list, topic_map[topic_key]))
                else:
                    weight_sentence_list.append((weight_word_list, 0))

            #print ">>%s<<" % paragraph
            #print sentence_list
            #print weight_sentence_list

            content_map[i] = weight_sentence_list
            issue_map[i] = create_issues(weight_sentence_list)

            if issue_map[i]['is_issue']: topic_tip = 1
    
    data = {
        "content_map": content_map,
        "article_id": article_id,
        "title": article.title,
        "issue_map": issue_map,
        "topic_tip": topic_tip
    }
    return render_template('topic_vis.html', data=data)

def create_issues(weighted_list):
    topic_count = 0
    irrelevant_count = 0
    irrelevance_list = []
    get_indexes = lambda x, xs: [i for (y, i) in zip(xs, range(len(xs))) if x == y]

    list, weight = zip(*weighted_list)
    total_length = len(weighted_list)
    
    #check topic issue
    #not_topic = weight.count(0) + weight.count(1)
    #topic_count = total_length - not_topic
    not_topic_list = set(get_indexes(0, weight)) | set(get_indexes(1, weight))
    topic_list = set([i for i in range(total_length)]) - not_topic_list
    topic_count = len(topic_list)

    #check relevant issue
    if topic_count:
        for not_topic_idx in not_topic_list:
            sentence = list[not_topic_idx]
            words, words_weight = zip(*sentence)
            not_relevance = words_weight.count(0) + words_weight.count(1)

            if len(sentence) - not_relevance == 0:
                irrelevant_count = irrelevant_count + 1
                irrelevance_list.append(not_topic_idx)

    irrelevant_count = len(irrelevance_list)
    if topic_count != 1: is_issue = 1
    else: is_issue = 0

    issues = {
        "topic": topic_count,
        "irrelevance": irrelevant_count,
        "irrelevance_list": irrelevance_list,
        "is_issue": is_issue
    }
    return issues


@vis_views.route('/peer_vis/<article_id>', methods=('GET','POST'))
def peer_vis(article_id):

    all_peer_annotations = DBQuery().get_peer_annotations_by_article_id(article_id)
    article = DBQuery().get_article_by_id(article_id)
    paragraphs = article.content.split("<BR>")

    topic_map = {}
    relevance_map = {}
    topic_list = []
    relevance_list = []
    for annotation in all_peer_annotations:
        all_topics = annotation.topic.split("|")
        topic_list.extend(all_topics)
        all_relevances = annotation.relevance.split("|")
        relevance_list.extend(all_relevances)

    for par_topic in set(topic_list):
        topic_map[par_topic] = topic_list.count(par_topic)

    for par_relevance in set(relevance_list):
        relevance_map[par_relevance] = relevance_list.count(par_relevance)
      
    article_id = int(article_id)
    article = DBQuery().get_article_by_id(article_id)
    content_map = {}
    issue_map={}

    topic_tip = 0
    for i, paragraph in enumerate(article.content.split("<BR>")):
        if paragraph:
            sentence_list = re.split(r'(?<=[^A-Z].[.?]) +(?=[A-Z])', paragraph)

            weight_sentence_list = []
            for j, sentence in enumerate(sentence_list):
                topic_key = "%d-%d" % (i, j)
                sentence = sentence.strip()
                word_list = sentence.split(" ")
                weight_word_list = []
                for k, word in enumerate(word_list):
                    word = word.strip()
                    relevance_key = "%d-%d-%d" % (i, j, k)
                    if(relevance_key in relevance_map):
                        weight_word_list.append((word, relevance_map[relevance_key]))
                    else:
                        weight_word_list.append((word, 0))

                if(topic_key in topic_map):
                    weight_sentence_list.append((weight_word_list, topic_map[topic_key]))
                else:
                    weight_sentence_list.append((weight_word_list, 0))

            content_map[i] = weight_sentence_list
            issue_map[i] = create_issues(weight_sentence_list)

            if issue_map[i]['is_issue']: topic_tip = 1

    data = {
        "content_map": content_map,
        "article_id": article_id,
        "title": article.title,
        "issue_map": issue_map,
        "topic_tip": topic_tip,
        "peer_count": len(all_peer_annotations)
    }
    return render_template('peer_vis.html', data=data)


#@vis_views.route('/coherence_vis', methods=('GET','POST'))
#def coherence_vis():
#    data={}
#    return render_template('coherence_vis.html', data=data)
#
