import re
import random
import string
from flask import Blueprint, Flask, request, render_template, redirect, url_for, jsonify
from crowdtask.dbquery import DBQuery

admin_views = Blueprint('admin_views', __name__, template_folder='templates')

@admin_views.route('/groundtruth/<article_id>')
def groundtruth(article_id):
    article = DBQuery().get_article_by_id(article_id)
    paragraphs = article.content.split("<BR>")
    
    content_map = {}
    for i, paragraph in enumerate(paragraphs):
      sentence_list = re.split(r'(?<=[^A-Z].[.?]) +(?=[A-Z])', paragraph)
      content_map[i] = sentence_list

    data = {
       "article_id": article.id, 
       "title": article.title,
       "content_map": content_map
    }

    return render_template('groundtruth.html', data=data)
