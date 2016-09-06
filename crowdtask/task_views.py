import re

from flask import Blueprint, Flask, request, render_template, redirect, url_for, jsonify
from enum import TaskType, Status
from crowdtask.dbquery import DBQuery
from experiment_errors import ExperimentError

task_views = Blueprint('task_views', __name__, template_folder='templates')

#preview sample
sample_article = "Gold, a precious metal, is prized for two important characteristics. First of all, gold has a lustrous beauty that is resistant to corrosion. Therefore, it is suitable for jewelry, coins, and ornamental purposes. Gold never needs to be polished and will remain beautiful forever. For example, a Macedonian coin remains as untarnished today as the day it was made 25 centuries ago. Another important characteristic of gold is its usefulness to industry and science. For many years, it has been used in hundreds of industrial applications, such as photography and dentistry. The most recent use of gold is in astronauts' suits. Astronauts wear gold-plated heat shields for protection when they go outside spaceships in space. In conclusion, gold is treasured not only for its beauty but also for its utility."
sample_essay = {
    "title":"Important qualities of a co-worker",
    "content": "We spend more time with our co-workers during weekdays than we do with our family. Thus, it's important for our co-workers to be the people we can get along with. In my opinion, there are certain characteristics that all good co-workers have in common. They are cooperative, considerate and humorous.<BR>We no longer observe now a time that worships individual merits with great enthusiasm. Everyone should cooperate with each other. Teamwork is curial to a business. A good co-worker is willing to contribute to the office community and not too stubborn to accept advice. He realizes the fact that if one's work is left not done in time, it may hold up everyone else.<BR>Besides, a good co-worker is very considerate. He may change his own schedule to accommodate another's emergency. He may be a sympathetic listener, comforting others when they are miserable.<BR>What is more, a good co-worker should have a sense of humor. His positive attitude may create a pleasant environment. When we are under the great stress of work, what we need most is not a delicious meal but merely a few good jokes to relax our nerve cells.<BR>What I have listed is not the complete set of characters of a good co-worker, however, we can feel how comfortable it is to get along with a good co-worker. Being a good co-worker is not difficult but really very necessary. Such ex- perience of being a good co-worker will definitely contribute to other aspects of life such as friendship and a healthy lifestyle."
}

'''@task_views.route('/mturk_success')
def mturk_success():
    verified_string = request.args.get('verified_string')
    assignment_id = request.args.get('assignment_id')
    worker_id = request.args.get('worker_id')
    hit_id = request.args.get('hit_id')
    using_sandbox = request.args.get('using_sandbox')

    data = {
        "verified_string": verified_string,
        "assignment_id": assignment_id,
        "worker_id": worker_id,
        "hit_id": hit_id,
        "using_sandbox": using_sandbox
    }
    return render_template('mturk_success.html', data=data)
'''

@task_views.route('/mturk',  methods=["GET", "POST"])
def mturkroute():
    if not ('hitId' in request.args and 'assignmentId' in request.args):
        raise ExperimentError('hit_assign_worker_id_not_set_in_mturk')

    if not ('task_type' in request.args):
        raise ExperimentError('task_not_existed')

    if not('using_sandbox' in request.args):
        raise ExperimentError('improper_inputs')

    hit_id = request.args['hitId']
    assignment_id = request.args['assignmentId']
    using_sandbox = request.args['using_sandbox']
    task_type = request.args['task_type']

    if(using_sandbox == "True" or using_sandbox == "true"):
        using_sandbox = True
    else:
        using_sandbox = False

    worker_id = None
    status = None
    is_hit_accepted = False

    if 'workerId' in request.args:
        is_hit_accepted = True
        worker_id = request.args['workerId']

    #get task by workerId and assignmentId to check if have already finished
    task = DBQuery().get_task_by_worker_assignment_id(worker_id, assignment_id)

    if not task:
        if not is_hit_accepted:
            #preview_mode, add preview_flat
            content = sample_article
            paragraph_idx = "0"

            if(task_type == TaskType.TOPIC):
                data = {
                    'worker_id': worker_id,
                    'article_id': "",
                    'title': "Gold",
                    'content': [content],
                    'verified_string': "",
                    'preview_flag': "1",
                    'hit_id': hit_id,
                    'assignment_id': assignment_id
                }
                return render_template('topic_task.html', data=data)
            elif(task_type == TaskType.RELEVANCE):
                paragraph_idx = int(paragraph_idx)
                content = sample_article

                #topic_map = {}
                topic_sentence_idx = 0
                #topic_map[paragraph_idx] = [topic_sentence_idx]

                #count_list = []
                sentence_list = re.split(r'(?<=[^A-Z].[.?]) +(?=[A-Z])', content)
                par_length = len(sentence_list)

                #if paragraph_idx in topic_map:
                #    count_list = [topic_map[paragraph_idx].count(j) for j in range(par_length)]
                #else:
                #    count_list = [0]*par_length

                data = {
                    'worker_id': worker_id,
                    'article_id': "",
                    'title': "Gold",
                    'paragraph_idx': paragraph_idx,
                    'sentence_list': sentence_list,
                    #'topic_sentence': count_list,
                    'verified_string': "",
                    'preview_flag': "1",
                    'hit_id': hit_id,
                    'assignment_id': assignment_id,

                    'topic_sentence_idx': topic_sentence_idx
                }

                return render_template('relevance_task.html', data=data)
            elif(task_type == TaskType.RELATION):

                sentence_list = re.split(r'(?<=[^A-Z].[.?]) +(?=[A-Z])', paragraph)

                data = {
                    'worker_id': worker_id,
                    'article_id': "",
                    'title': "Gold",
                    'sentence_list': sentence_list,
                    'paragraph_idx': paragraph_idx,
                    'verified_string': "",
                    'preview_flag': "1",
                    'hit_id': hit_id,
                    'assignment_id': assignment_id
                }
                return render_template('relation_task.html', data=data)

            elif(task_type == TaskType.LINK):
                title = sample_essay["title"]
                content = sample_essay["content"]
                preview_flag = "1"
                thesis_statement_idx = "0-0"
                topic_sentence_ids = "1-0|2-0"

                paragraph_map = {}
                
                for i, paragraph in enumerate(content.split("<BR>")):
                    if paragraph:
                        sentence_list = re.split(r'(?<=[^A-Z].[.?]) +(?=[A-Z])', paragraph)
                        paragraph_map[i] = sentence_list

                thesis_statement = tuple(map(int, thesis_statement_idx.split("-")))
                all_topic_sentences = [ tuple(map(int,topic.split("-"))) for topic in topic_sentence_ids.split("|")]
                
                data = {
                    'worker_id': worker_id,
                    'article_id': "",
                    'title': title,

                    'thesis_statement_idx': thesis_statement_idx,
                    'topic_sentence_ids': topic_sentence_ids,
                    'paragraph_map': paragraph_map,
                    'thesis_statement': thesis_statement,
                    'all_topic_sentences': all_topic_sentences,
                        
                    'preview_flag': "1",
                    'verified_string': "",
                    'hit_id': hit_id,
                    'assignment_id': assignment_id,
                }

                return render_template('link_task.html', data=data)

        else:
            return render_template('mturkindex.html', param=request.args.to_dict())
    else:
        data = {
            'hit_id': hit_id,
            'assignment_id': assignment_id,
            'worker_id': worker_id,
            'using_sandbox': using_sandbox
        }
        return render_template('complete.html', data=data)


@task_views.route('/welcome', methods=["GET", "POST"])
def welcome():
    if not ('hitId' in request.args and 'workerId' in request.args
        and 'assignmentId' in request.args and 'task_type' in request.args):
        raise ExperimentError('hit_assign_worker_id_not_set_in_mturk')

    #hit_id = request.args['hitId']
    #assignment_id = request.args['assignmentId']
    task_type = request.args['task_type']
    #article_id = request.args.get('article_id',u'0')

    if(task_type == TaskType.TOPIC):
        return redirect(
            url_for('views.topic_task', **request.args.to_dict()))

    elif(task_type == TaskType.RELEVANCE):
        return redirect(
            url_for('views.relevance_task', **request.args.to_dict()))
    elif(task_type == TaskType.RELATION):
        return redirect(
            url_for('views.relation_task', **request.args.to_dict()))
    elif(task_type == TaskType.LINK):
        return redirect(
            url_for('views.link_task', **request.args.to_dict()))
    else:
        raise ExperimentError('task_not_existed')

@task_views.route('/closepopup', methods=["GET", "POST"])
def closepopup():
    worker_id = request.args.get('workerId',u'')
    hit_id = request.args.get('hitId',u'')
    assignment_id = request.args.get('assignmentId',u'')

    #update status
    DBQuery().update_task_status_by_worker_assignment_id(worker_id, assignment_id, Status.FINISH)
    return render_template("closepopup.html")

@task_views.errorhandler(ExperimentError)
def handleExpError(e):
    """Handle errors by sending an error page."""
    return e.error_page(request)
