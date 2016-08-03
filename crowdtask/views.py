import random
import string
from flask import Blueprint, Flask, request, render_template, redirect, url_for, jsonify
from crowdtask.dbquery import DBQuery

views = Blueprint('views', __name__, template_folder='templates')
sample_article = "Gold, a precious metal, is prized for two important characteristics. First of all, gold has a lustrous beauty that is resistant to corrosion. Therefore, it is suitable for jewelry, coins, and ornamental purposes. Gold never needs to be polished and will remain beautiful forever. For example, a Macedonian coin remains as untarnished today as the day it was made 25 centuries ago. Another important characteristic of gold is its usefulness to industry and science. For many years, it has been used in hundreds of industrial applications, such as photography and dentistry. The most recent use of gold is in astronauts' suits. Astronauts wear gold-plated heat shields for protection when they go outside spaceships in space. In conclusion, gold is treasured not only for its beauty but also for its utility."
sample_essay = {
    "title":"Important qualities of a co-worker",
    "content": "We spend more time with our co-workers during weekdays than we do with our family. Thus, it's important for our co-workers to be the people we can get along with. In my opinion, there are certain characteristics that all good co-workers have in common. They are cooperative, considerate and humorous.<BR>We no longer observe now a time that worships individual merits with great enthusiasm. Everyone should cooperate with each other. Teamwork is curial to a business. A good co-worker is willing to contribute to the office community and not too stubborn to accept advice. He realizes the fact that if one's work is left not done in time, it may hold up everyone else.<BR>Besides, a good co-worker is very considerate. He may change his own schedule to accommodate another's emergency. He may be a sympathetic listener, comforting others when they are miserable.<BR>What is more, a good co-worker should have a sense of humor. His positive attitude may create a pleasant environment. When we are under the great stress of work, what we need most is not a delicious meal but merely a few good jokes to relax our nerve cells.<BR>What I have listed is not the complete set of characters of a good co-worker, however, we can feel how comfortable it is to get along with a good co-worker. Being a good co-worker is not difficult but really very necessary. Such ex- perience of being a good co-worker will definitely contribute to other aspects of life such as friendship and a healthy lifestyle."
}
@views.route('/')
def index():
    return render_template('index.html')

@views.route('/topic', methods=('GET','POST'))
def topic_task():

    paragraph_idx = None
    article_id = None
    article = None

    worker_id = request.args.get('workerId', u'tester')
    paragraph_idx = request.args.get('paragraph_idx')
    preview_flag = request.args.get('preview_flag')

    
    if request.args.has_key('article_id'):
        article_id = request.args.get('article_id')
        article = DBQuery().get_article_by_id(article_id)

    #mturk stuff
    assignment_id = request.args.get('assignmentId', u'')
    hit_id = request.args.get('hitId', u'')

    verified_string = generate_verified_str(6)

    if article and preview_flag != "1":
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
            'worker_id': worker_id,
            'article_id': article_id,
            'title': article.title,
            'content': content,
            'paragraph_idx': paragraph_idx,
            'verified_string': verified_string,
            'hit_id': hit_id,
            'assignment_id': assignment_id
        }
    else:
        data = {
            'worker_id': worker_id,
            'article_id': article_id,
            'title': "Gold",
            'content': [sample_article],
            'paragraph_idx': "",
            'verified_string': verified_string,
            'preview_flag': preview_flag,
            'hit_id': hit_id,
            'assignment_id': assignment_id
        }
    
    return render_template('topic_task.html', data=data)

@views.route('/relevance', methods=('GET','POST'))
def relevance_task():
    article_id = None
    article = None
    paragraph_idx = None

    worker_id = request.args.get('workerId',u'tester')
    paragraph_idx = request.args.get('paragraph_idx')

    
    if request.args.has_key('article_id'):
        article_id = request.args.get('article_id')
        article = DBQuery().get_article_by_id(article_id)

    #mturk stuff
    assignment_id = request.args.get('assignmentId', u'')
    hit_id = request.args.get('hitId', u'')

    verified_string = generate_verified_str(6)

    if article and paragraph_idx:
        paragraph_map = {}
        for i, paragraph in enumerate(article.content.split("<BR>")):
            if paragraph:
                paragraph_map[i] = paragraph

        paragraph_idx = int(paragraph_idx)
        if paragraph_idx >= len(paragraph_map):
            paragraph_idx = 0


        #convert paragraph content to sentence list
        content = paragraph_map[paragraph_idx]
        sentence_list = content.split(".")
        sentence_list = sentence_list[:-1]
        par_length = len(sentence_list)

        #if no input, retrieve database
        topic_sentence_idx = None
        if not request.args.has_key('topic_sentence_idx'):
            topics = DBQuery().get_topics_by_article_paragraph_id(article_id, paragraph_idx)
            topic_map = []
            for topic in topics:
                topic_map.extend([int(i) for i in topic.topic_sentence_ids.split(",")])
        
            count_list = [topic_map.count(j) for j in range(par_length)]

            #filter - only keep the max value, and clear up the remaining value
            topic_sentence = [0]*par_length
            

            if max(count_list) >= 2:
                topic_sentence[count_list.index(max(count_list))] = count_list[count_list.index(max(count_list))]
                topic_sentence_idx = count_list.index(max(count_list))
        else:
            if request.args.get('topic_sentence_idx').isdigit():
                topic_sentence_idx = int(request.args.get('topic_sentence_idx'))            
        
        data = {
            'worker_id': worker_id,
            'article_id': article_id,
            'title': article.title,
            'paragraph_idx': paragraph_idx,
            'sentence_list': sentence_list,
            #'topic_sentence': topic_sentence,
            'verified_string': verified_string,
            'hit_id': hit_id,
            'assignment_id': assignment_id,

            #not use yet
            'topic_sentence_idx': topic_sentence_idx
        }
    else:
        #sample
        paragraph_idx = 0
        topic_sentence_idx = 0
        
        topic_map = {}
        topic_sentence_ids = "0"
        topic_map[paragraph_idx] = [int(i) for i in topic_sentence_ids.split(",")]
        
        count_list = []
        sentence_list = []
        
        content = sample_article
        sentence_list = content.split(".")
        sentence_list = sentence_list[:-1]
        par_length = len(sentence_list)
        
        if paragraph_idx in topic_map:
            count_list = [topic_map[paragraph_idx].count(j) for j in range(par_length)]
        else:
            count_list = [0]*par_length

        data = {
            'worker_id': worker_id,
            'article_id': article_id,
            'title': "Gold",
            'paragraph_idx': paragraph_idx,
            'sentence_list': sentence_list,
            'topic_sentence': count_list,
            'verified_string': "",
            'preview_flag': "1",
            'hit_id': hit_id,
            'assignment_id': assignment_id,

            'topic_sentence_idx': topic_sentence_idx
        }

    return render_template('relevance_task.html', data=data)
    
@views.route('/relation', methods=('GET','POST'))
def relation_task():
    worker_id = request.args.get('workerId',u'tester')
    paragraph_idx = request.args.get('paragraph_idx', u'0')

    article_id = None
    article = None
    if request.args.has_key('article_id'):
        article_id = request.args.get('article_id')
        article = DBQuery().get_article_by_id(article_id)

    #mturk stuff
    assignment_id = request.args.get('assignmentId', u'')
    hit_id = request.args.get('hitId', u'')

    verified_string = generate_verified_str(6)

    if article:

        paragraph_map = {}
        for i, paragraph in enumerate(article.content.split("<BR>")):
            if paragraph:
                paragraph_map[i] = paragraph

        # set one paragraph (should modify, solved it temporary)
        paragraph_idx = int(paragraph_idx)
        if paragraph_idx >= len(paragraph_map):
            paragraph_idx = 0

        content = paragraph_map[paragraph_idx]
        sentence_list = content.split(".")
        sentence_list = sentence_list[:-1]

            
        data = {
            'worker_id': worker_id,
            'article_id': article_id,
            'title': article.title,
            'sentence_list': sentence_list,
            'paragraph_idx': paragraph_idx, #diff from topic
            'verified_string': verified_string,
            'hit_id': hit_id,
            'assignment_id': assignment_id
        }

    else:
        paragraph_idx = int(paragraph_idx)

        content = sample_article
        sentence_list = content.split(".")
        sentence_list = sentence_list[:-1]

        data = {
            'worker_id': worker_id,
            'article_id': "",
            'title': "Gold",
            'sentence_list': sentence_list,
            'paragraph_idx': paragraph_idx, #diff from topic
            'verified_string': verified_string,
            'preview_flag': "1",
            'hit_id': hit_id,
            'assignment_id': assignment_id
        }

    return render_template('relation_task.html', data=data)

@views.route('/link', methods=('GET','POST'))
def link_task():
    article_id = None
    article = None


    worker_id = request.args.get('workerId',u'tester')
    verified_string = generate_verified_str(6)

    thesis_statement_idx = request.args.get('thesis_statement_idx',u'0-0') #0-0 (#paragraph_idx,#topic_sentence_idx)

    #mturk stuff
    assignment_id = request.args.get('assignmentId', u'')
    hit_id = request.args.get('hitId', u'')

    if request.args.has_key('article_id'):
        article_id = request.args.get('article_id')
        article = DBQuery().get_article_by_id(article_id)    

    if request.args.has_key('topic_sentence_ids'):
        topic_sentence_ids = request.args.get('topic_sentence_ids') #1-1|2-0 (at least two elements)
    else:
        topic_sentence_ids = "1-0|2-0"

    if article:
        content = article.content
        title = article.title

    else:
        #sample
        title = sample_essay["title"]
        content = sample_essay["content"]
        preview_flag = "1"

    # ----------------------
    # paragraph_map structure
    # paragraph_map = {
    #   0: [sentence_0, sentence_1, sentence_2],
    #   1: [sentence_0, sentence_1, sentence_2],
    #   2: [sentence_0, sentence_1, sentence_2]
    # }
    # ----------------------

    paragraph_map = {}
    thesis_statement = None
    all_topic_sentences = []
    for i, paragraph in enumerate(content.split("<BR>")):
        if paragraph:
            sentence_list = paragraph.split(".")
            sentence_list = sentence_list[:-1]
            paragraph_map[i] = sentence_list


    #if no input, retrieve database
    if article and not request.args.has_key('topic_sentence_ids'):

        for paragraph_idx in range(len(paragraph_map)):
            topic_sentence_idx = None
            topics = DBQuery().get_topics_by_article_paragraph_id(article_id, paragraph_idx)

            topic_map = []
            for topic in topics:
                topic_map.extend([int(i) for i in topic.topic_sentence_ids.split(",")])
            
            par_length = len(paragraph_map[paragraph_idx])
            count_list = [topic_map.count(j) for j in range(par_length)]

            #filter - only keep the max value, and clear up the remaining value
            topic_sentence = [0]*par_length

            if max(count_list) >= 2:
                topic_sentence[count_list.index(max(count_list))] = count_list[count_list.index(max(count_list))]
                topic_sentence_idx = count_list.index(max(count_list))

            if topic_sentence_idx != None:
                if paragraph_idx == 0:
                    thesis_statement = (paragraph_idx, topic_sentence_idx)
                else:
                    all_topic_sentences.append((paragraph_idx, topic_sentence_idx))

    else:
        
        thesis_statement = tuple(map(int, thesis_statement_idx.split("-")))
        all_topic_sentences = [ tuple(map(int,topic.split("-"))) for topic in topic_sentence_ids.split("|")]

    print "article_id: %s" % article_id
    print "+++++++"
    print thesis_statement
    print all_topic_sentences
    print "+++++++"

    data = {
        'worker_id': worker_id,
        'article_id': article_id,
        'title': title,

        'thesis_statement_idx': thesis_statement_idx,
        'topic_sentence_ids': topic_sentence_ids,
        'paragraph_map': paragraph_map,
        'thesis_statement': thesis_statement,
        'all_topic_sentences': all_topic_sentences,
            
        'verified_string': verified_string,
        'hit_id': hit_id,
        'assignment_id': assignment_id,
    }

    if not article:
        data['preview_flag'] = preview_flag
        data['verified_string'] = ""

    
    return render_template('link_task.html', data=data)


@views.route('/all')
def show_all():
    all_articles = DBQuery().get_all_articles();

    article_authors = "anonymous"
    data_list = []
    for article in all_articles:
        article_id = article.id
        title = article.title.encode("utf-8")

        if article.authors:
            article_authors = article.authors
        
        data = {
            "title": title,
            "article_id": article_id,
            "authors": article_authors
        }
        data_list.append(data)

    return render_template('show_all.html', data=data_list)

@views.route('/article/<article_id>')
def show_article(article_id):
    article = DBQuery().get_article_by_id(article_id)
    paragraphs = DBQuery().get_paragraphs_by_article_id(article_id)
    workflows = DBQuery().get_workflows_by_article_id(article_id)
    workflow_list = [str(workflow.id) for workflow in workflows]

    list = []
    for par in paragraphs:
        list.append((par.paragraph_idx, par.content))

    sorted(list)
    data = {
       "id": article.id, 
       "title": article.title,
       "paragraphs": list,
       "workflow_list": workflow_list
    }

    return render_template('article.html', data=data)

@views.route('/success')
def success():
    verified_string = request.args.get('verified_string')
    if not verified_string:
        data = {}
    else:
        data = {
            "verified_string": verified_string
        }
    return render_template('success.html', data=data)


def generate_verified_str(number):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(number))

# error page
@views.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@views.app_errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400
