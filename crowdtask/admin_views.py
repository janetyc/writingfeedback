import re
import random
import string
from flask import Blueprint, Flask, request, render_template, redirect, url_for, jsonify
from crowdtask.dbquery import DBQuery

admin_views = Blueprint('admin_views', __name__, template_folder='templates')


@admin_views.route('/groundtruth/<article_id>', methods=('GET','POST'))
def groundtruth(article_id):
    golden_id = None
    if 'golden_id' in request.args:
      golden_id = request.args["golden_id"]  

    all_golden_structures = DBQuery().get_golden_structures_by_article_id(article_id)
    all_goldens = [item.id for item in all_golden_structures]

    article = DBQuery().get_article_by_id(article_id)
    paragraphs = article.content.split("<BR>")
    
    if golden_id:
      goldenstructure = DBQuery().get_golden_structure_by_id(golden_id)
      all_topics = goldenstructure.topic.split("|")
      all_relevances = goldenstructure.relevance.split("|")
    else:
      all_topics = None
      all_relevances = None

    relevance_map = {}
    topic_map = {}
    content_map = {}
    for i, paragraph in enumerate(paragraphs):
      sentence_list = re.split(r'(?<=[^A-Z].[.?]) +(?=[A-Z])', paragraph)
      content_map[i] = sentence_list
      if all_topics:
        topic_map[i] = [1 if "%d-%d" % (i, j) in all_topics else 0 for j in range(len(sentence_list))]
      else:
        topic_map[i] = [0]*len(sentence_list)

      #print topic_map[i]

      relevance_map[i]=[]
      for j, sentence in enumerate(sentence_list):
        words = sentence.split(" ")
        if all_relevances:
          list = [1 if "%d-%d-%d" % (i, j, k) in all_relevances else 0 for k in range(len(words))]
        else:
          list = [0]*len(words)

        relevance_map[i].append(list)

      #print relevance_map[i]

    data = {
       "article_id": article.id, 
       "title": article.title,
       "content_map": content_map,
       "all_goldens": all_goldens,
       "topic_map": topic_map,
       "relevance_map": relevance_map
    }

    return render_template('groundtruth.html', data=data)

@admin_views.route('/get_groundtruth_json/<article_id>', methods=('GET','POST'))
def get_groundtruth_json(article_id):
    golden_id = None
    all_golden_structures = DBQuery().get_golden_structures_by_article_id(article_id)
    
    data = {}
    for golden in all_golden_structures:
      all_topics = ["%s-%s" % (article_id,i) for i in golden.topic.split("|")]
      all_relevances = ["%s-%s" % (article_id,i) for i in golden.relevance.split("|")]
      data[golden.id] = {
        "article_id": article_id, 
        "golden_topics": all_topics,
        "golden_relevance": all_relevances
      }

    return jsonify(success=1, data=data)