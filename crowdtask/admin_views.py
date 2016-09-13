#!/usr/bin/python
 # -*- coding: utf-8 -*-

import re
import random
import string
from flask import Blueprint, Flask, request, render_template, redirect, url_for, jsonify
from crowdtask.dbquery import DBQuery

admin_views = Blueprint('admin_views', __name__, template_folder='templates')

#for remmote server
exp_data = {
  "P1": {
    "name": u"劉縣璇",
    "data": [("v3",41)]
  },
  "P2": {
    "name": u"黃小菱",
    "data": [("v2",34)]
  },
  "P3": {
    "name": u"許佳汎",
    "data": []
  },
  "P4": {
    "name": u"蕭佳倩",
    "data": [("v2",30)]
  },
  "P5": {
    "name": u"尹紹安",
    "data": [("v1",40)]
  },
  "P6": {
    "name": u"彭寶賢",
    "data": [("v1",31)]
  },
  "P7": {
    "name": u"王昱丹",
    "data": [("v3",46)]
  },
  "P8": {
    "name": u"曾梓婷",
    "data": [("v2",38)]
  },
  "P9": {
    "name": u"詹穆彥",
    "data": [("v3",43)]
  },
  "P10": {
    "name": u"童安弘",
    "data": [("v2",35)]
  },
  "P11": {
    "name": u"陳昭碩",
    "data": [("v1",44)]
  },
  "P12": {
    "name": u"陳宗葆",
    "data": [("v1",29)]
  },
  "P13": {
    "name": u"黃琮仁",
    "data": []
  },
  "P14": {
    "name": u"Sean",
    "data": [("v2",36)]
  },
  "P15": {
    "name": u"李倧輔",
    "data": []
  },
  "P16": {
    "name": u"楊珮綺",
    "data": [("v2",42)]
  },
  "P17": {
    "name": u"林家興",
    "data": [("v1",32)]
  },
  "P18": {
    "name": u"黃鈺雯",
    "data": [("v1",33)]
  }
}

@admin_views.route('/experiment')
def experiment():
  data = exp_data
  return render_template('experiment.html', data=data)

@admin_views.route('/groundtruth/<article_id>', methods=('GET','POST'))
def groundtruth(article_id):
    golden_id = None
    if 'golden_id' in request.args:
      golden_id = request.args["golden_id"]  

    all_golden_structures = DBQuery().get_golden_structures_by_article_id(article_id)
    all_goldens = [item.id for item in all_golden_structures]

    article = DBQuery().get_article_by_id(article_id)
    paragraphs = article.content.split("<BR>")
    
    all_topics = None
    all_relevances = None
    all_irrelevances = None
    if golden_id:
      goldenstructure = DBQuery().get_golden_structure_by_id(golden_id)
      all_topics = goldenstructure.topic.split("|")
      all_relevances = goldenstructure.relevance.split("|")
      if goldenstructure.irrelevance: all_irrelevances = goldenstructure.irrelevance.split("|")

    relevance_map = {}
    topic_map = {}
    irrelevance_map = {}
    content_map = {}
    for i, paragraph in enumerate(paragraphs):
      sentence_list = re.split(r'(?<=[^A-Z].[.?]) +(?=[A-Z])', paragraph)
      content_map[i] = sentence_list
      if all_topics:
        topic_map[i] = [1 if "%d-%d" % (i, j) in all_topics else 0 for j in range(len(sentence_list))]
      else:
        topic_map[i] = [0]*len(sentence_list)

      #print topic_map[i]

      if all_irrelevances:
        irrelevance_map[i] = [1 if "%d-%d" % (i, j) in all_irrelevances else 0 for j in range(len(sentence_list))]
      else:
        irrelevance_map[i] = [0]*len(sentence_list)

      #print irrelevance_map[i]


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
       "authors": article.authors,
       "content_map": content_map,
       "all_goldens": all_goldens,
       "topic_map": topic_map,
       "relevance_map": relevance_map,
       "irrelevance_map": irrelevance_map
    }

    return render_template('groundtruth.html', data=data)

@admin_views.route('/get_groundtruth_json/<article_id>', methods=('GET','POST'))
def get_groundtruth_json(article_id):
    golden_id = None
    all_golden_structures = DBQuery().get_golden_structures_by_article_id(article_id)
    
    data = {}
    for golden in all_golden_structures:
      all_topics = ["%s-%s" % (article_id,i) for i in golden.topic.split("|")]
      if golden.irrelevance:
        all_irrelevances = ["%s-%s" % (article_id,i) for i in golden.irrelevance.split("|")]
      else:
        all_irrelevances = []
      all_relevances = ["%s-%s" % (article_id,i) for i in golden.relevance.split("|")]
      
      data[golden.id] = {
        "created_user": golden.created_user,
        "article_id": article_id, 
        "golden_topics": all_topics,
        "golden_irrelevances": all_irrelevances,
        "golden_relevances": all_relevances
      }

    return jsonify(success=1, data=data)