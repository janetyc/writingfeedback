from flask import Blueprint, Flask, request, render_template, redirect, url_for, jsonify
from enum import TaskType, Status
from crowdtask.dbquery import DBQuery
from experiment_errors import ExperimentError

task_views = Blueprint('task_views', __name__, template_folder='templates')

#preview sample
sample_article = "Gold, a precious metal, is prized for two important characteristics. First of all, gold has a lustrous beauty that is resistant to corrosion. Therefore, it is suitable for jewelry, coins, and ornamental purposes. Gold never needs to be polished and will remain beautiful forever. For example, a Macedonian coin remains as untarnished today as the day it was made 25 centuries ago. Another important characteristic of gold is its usefulness to industry and science. For many years, it has been used in hundreds of industrial applications, such as photography and dentistry. The most recent use of gold is in astronauts' suits. Astronauts wear gold-plated heat shields for protection when they go outside spaceships in space. In conclusion, gold is treasured not only for its beauty but also for its utility."


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
    if not (request.args.has_key('hitId') and request.args.has_key('assignmentId')):
        raise ExperimentError('hit_assign_worker_id_not_set_in_mturk')

    if not (request.args.has_key('task_type')):
        raise ExperimentError('task_not_existed')

    if not(request.args.has_key('using_sandbox')):
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

    if request.args.has_key('workerId'):
        is_hit_accepted = True
        worker_id = request.args['workerId']

    #get task by workerId and assignmentId to check if have already finished
    task = DBQuery().get_task_by_worker_assignment_id(worker_id ,assignment_id)

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

                topic_map = {}
                topic_sentence_ids = "0"
                topic_map[paragraph_idx] = [int(i) for i in topic_sentence_ids.split(",")]
        
                count_list = []
                sentence_list = []
        
                sentence_list = content.split(".")
                sentence_list = sentence_list[:-1]
                par_length = len(sentence_list)
        
                if paragraph_idx in topic_map:
                    count_list = [topic_map[paragraph_idx].count(j) for j in range(par_length)]
                else:
                    count_list = [0]*par_length

                data = {
                    'worker_id': worker_id,
                    'article_id': "",
                    'title': "Gold",
                    'paragraph_idx': paragraph_idx,
                    'sentence_list': sentence_list,
                    'topic_sentence': count_list,
                    'verified_string': "",
                    'preview_flag': "1",
                    'hit_id': hit_id,
                    'assignment_id': assignment_id
                }

                return render_template('relevance_task.html', data=data)
            elif(task_type == TaskType.RELATION):

                sentence_list = content.split(".")
                sentence_list = sentence_list[:-1]

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
    if not (request.args.has_key('hitId') and request.args.has_key('workerId') 
        and request.args.has_key('assignmentId') and request.args.has_key('task_type')):
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