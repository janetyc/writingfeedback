from flask import Blueprint, Flask, request, render_template, redirect, url_for, jsonify
from crowdtask.dbquery import DBQuery

views = Blueprint('views', __name__, template_folder='templates')


@views.route('/')
def index():
    return render_template('index.html')

@views.route('/topic/<int:article_id>', methods=('GET','POST'))
def topic_task(article_id):
    paragraph_idx = request.args.get('paragraph_idx',u'0')
    article = DBQuery().get_article_by_id(article_id)
    if article:
        paragraphs = {}
        for i, paragraph in enumerate(article.content.split("<BR>")):
            if paragraph:
                paragraphs[i] = paragraph

        content = paragraphs.values()
        
        #if paragraph_idx:
        #    paragraph_idx = int(paragraph_idx)
        #    if paragraph_idx and ( paragraph_idx < len(paragraphs.values()) ):
        #        content = [paragraphs[paragraph_idx]]

        data = {
            'article_id': article_id,
            'title': article.title,
            'content': content,
            'paragraph_idx': paragraph_idx
        }
    else:
        data = {
            'article_id': article_id,
            'title': "",
            'content': [],
            'paragraph_idx': ""
        }
    
    return render_template('topic_task.html', data=data)

@views.route('/relevance/<int:article_id>', methods=('GET','POST'))
def relevance_task(article_id):
    paragraph_idx = request.args.get('paragraph_idx',u'0')
    article = DBQuery().get_article_by_id(article_id)

    if article:
        paragraph_map = {}
        for i, paragraph in enumerate(article.content.split("<BR>")):
            if paragraph:
                paragraph_map[i] = paragraph

        # set one paragraph (should modify, solved it temporary)
        paragraphs = {}
        paragraph_idx = int(paragraph_idx)
        if paragraph_idx < len(paragraph_map):
            paragraphs[paragraph_idx] = paragraph_map[paragraph_idx]

        topics = DBQuery().get_topics_by_article_id(article_id)
        topic_map = {}
        for topic in topics:
            if not topic.paragraph_idx in topic_map:
                topic_map[topic.paragraph_idx] = []

            topic_map[topic.paragraph_idx].extend([int(i) for i in topic.topic_sentence_ids.split(",")])


        count_list = []
        sentences_list = []

        for i in range(len(paragraphs)):
            lines = paragraphs[i].split(".")
            lines = lines[:-1]
            par_length = len(lines)
            sentences_list.append(lines)
            if i in topic_map:
                count_list.append([topic_map[i].count(j) for j in range(par_length)])
            else:
                count_list.append([0]*par_length)


        #print topic_map
        #print count_list
        #print sentences_list

        data = {
            'article_id': article_id,
            'title': article.title,
            'paragraphs': sentences_list,
            'topic_sentence': count_list
        }
    else:
        data = {
            'article_id': article_id,
            'title': [],
            'paragraphs': [],
            'topic_sentence': []
        }
    return render_template('relevance_task.html', data=data)
    
@views.route('/relation/<int:article_id>', methods=('GET','POST'))
def relation_task(article_id):
    paragraph_idx = request.args.get('paragraph_idx', u'0')
    article = DBQuery().get_article_by_id(article_id)

    if article:
        paragraph_map = {}
        paragraphs = {}
        for i, paragraph in enumerate(article.content.split("<BR>")):
            if paragraph:
                sentence_list = paragraph.split(".")
                paragraph_map[i] = sentence_list[:-1]
        
        # set one paragraph (should modify, solved it temporary)
        paragraph_idx = int(paragraph_idx)
        if paragraph_idx < len(paragraph_map):
            paragraphs[paragraph_idx] = paragraph_map[paragraph_idx]
            
        data = {
            'article_id': article_id,
            'title': article.title,
            'paragraphs': paragraphs,
            'paragraph_idx': paragraph_idx
        }


    else:
        data = {
            'article_id': article_id,
            'title': "",
            'paragraphs': [],
            'paragraph_idx': paragraph_idx
        }

    return render_template('relation_task.html', data=data)

@views.route('/all')
def show_all():
    all_articles = DBQuery().get_all_articles();

    data_list = []
    for article in all_articles:
        article_id = article.id
        title = article.title.encode("utf-8")
        
        data = {
            "title": title,
            "article_id": article_id
        }
        data_list.append(data)

    return render_template('show_all.html', data=data_list)

@views.route('/article/<article_id>')
def show_article(article_id):
    article = DBQuery().get_article_by_id(article_id)
    paragraphs = DBQuery().get_paragraphs_by_article_id(article_id)

    list = []
    for par in paragraphs:
        list.append((par.paragraph_idx, par.content))

    sorted(list)
    data = {
       "id": article.id, 
       "title": article.title,
       "paragraphs": list
    }

    return render_template('article.html', data=data)

@views.route('/success')
def success():
    return render_template('success.html')

# error page
@views.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@views.app_errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400
