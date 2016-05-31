import random
import string
from flask import Blueprint, Flask, request, render_template, redirect, url_for, jsonify
from crowdtask.dbquery import DBQuery

vis_views = Blueprint('vis_views', __name__, template_folder='templates')

@vis_views.route('/topic_vis', methods=('GET','POST'))
def topic_vis():
    data = {}
    topic_map = {}
    relevance_map = {}
    if not (request.args.has_key('workflow_id')):
        data = {}
        return render_template('topic_vis.html', data)
    
    workflow_id = request.args.get('workflow_id')
    workflow = DBQuery().get_workflow_by_id(workflow_id)
    article_ids = []
    if workflow.topic_hit_ids != "":
        topic_hits = workflow.topic_hit_ids.split(",")
        for hit_id in topic_hits:
            topic_list = DBQuery().get_topics_by_hit_id(hit_id)

            for par_topic in set(topic_list):
                article_ids.append(par_topic[0].split("-")[0])
                key = "-".join(par_topic)
                topic_map[key] = topic_list.count(par_topic)

    if workflow.relevance_hit_ids != "":
        relevance_hits = workflow.relevance_hit_ids.split(",")
        for hit_id in relevance_hits:
            relevance_list = DBQuery().get_relevances_by_hit_id(hit_id)

            for par_relevance in set(relevance_list):
                # paragraph_idx-sentence_idx-word_idx
                print par_relevance
                key = "%d-%d-%s" % (par_relevance[0],par_relevance[1],par_relevance[2])
                relevance_map[key] = relevance_list.count(par_relevance)


    article_ids = set(article_ids)
    if not len(article_ids):
        data = {}
        return render_template('topic_vis.html', data=data)

    article_id = int(article_ids.pop())

    article = DBQuery().get_article_by_id(article_id)
    content_map = {}

    for i, paragraph in enumerate(article.content.split("<BR>")):
        if paragraph:
            sentence_list = paragraph.split(".")
            sentence_list = sentence_list[:-1]

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

            content_map[i] = weight_sentence_list


    data = {
        "content_map": content_map,
        "article_id": article_id,
        "title": article.title
    }
    return render_template('topic_vis.html', data=data)


#@vis_views.route('/coherence_vis', methods=('GET','POST'))
#def coherence_vis():
#    data={}
#    return render_template('coherence_vis.html', data=data)
#
