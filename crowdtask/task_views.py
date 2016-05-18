from flask import Blueprint, Flask, request, render_template, redirect, url_for, jsonify
from enum import TaskType, Status
from crowdtask.dbquery import DBQuery

task_views = Blueprint('task_views', __name__, template_folder='templates')


experiment_errors = dict(
    status_incorrectly_set=1000,
    hit_assign_worker_id_not_set_in_mturk=1001,
    hit_assign_worker_id_not_set_in_consent=1002,
    hit_assign_worker_id_not_set_in_exp=1003,
    hit_assign_appears_in_database_more_than_once=1004,
    already_started_exp=1008,
    already_started_exp_mturk=1009,
    already_did_exp_hit=1010,
    tried_to_quit=1011,
    intermediate_save=1012,
    improper_inputs=1013,
    page_not_found=404,
    in_debug=2005,
    task_not_existed=1014,
    unknown_error=9999
)

class ExperimentError(Exception):

    """
    Error class for experimental errors, such as subject not being found in
    the database.
    """

    def __init__(self, value):
        self.value = value
        self.errornum = experiment_errors[self.value]

    def __str__(self):
        return repr(self.value)

    def error_page(self, request):
        return render_template('error.html',
                               errornum=self.errornum,
                               **request.args)

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

    if not (request.args.has_key('taskType')):
        raise ExperimentError('task_not_existed')

    if not(request.args.has_key('using_sandbox')):
        raise ExperimentError('improper_inputs')

    hitId = request.args['hitId']
    assignmentId = request.args['assignmentId']
    using_sandbox = request.args['using_sandbox']

    if(using_sandbox == "True" or using_sandbox == "true"):
        using_sandbox = True
    else:
        using_sandbox = False

    workerId = None
    status = None
    is_hit_accepted = False

    if request.args.has_key('workerId'):
        is_hit_accepted = True
        workerId = request.args['workerId']

    taskType = request.args.get('taskType', TaskType.TOPIC)

    #get task by workerId and assignmentId to check if have already finished
    task = DBQuery().get_task_by_worker_assignment_id(workerId ,assignmentId)

    if not task:
        if not is_hit_accepted:
            #preview_mode, add preview_flat
            return redirect(
                url_for('views.topic_task', preview_flag='1', **request.args.to_dict()))
        else:
            return render_template('mturkindex.html', assignmentId=assignmentId, param=request.args.to_dict())
    else:
        return render_template('complete.html', hitId=hitId, assignmentId=assignmentId,
            workerId=workerId, using_sandbox=using_sandbox)


@task_views.route('/welcome', methods=["GET", "POST"])
def welcome():
    if not (request.args.has_key('hitId') and request.args.has_key('workerId') 
        and request.args.has_key('assignmentId') and request.args.has_key('taskType')):
        raise ExperimentError('hit_assign_worker_id_not_set_in_mturk')

    hitId = request.args['hitId']
    assignmentId = request.args['assignmentId']
    taskType = request.args['taskType']
    
    if(taskType == TaskType.TOPIC):
        article_id = request.args.get('article_id')
        return redirect(
            url_for('views.topic_task', **request.args.to_dict()))
    else:
        raise ExperimentError('task_not_existed')

@task_views.route('/closepopup', methods=["GET", "POST"])
def closepopup():
    #update status
    print request.args

    workerId = request.args.get('workerId',u'')
    hitId = request.args.get('hitId',u'')
    assignmentId = request.args.get('assignmentId',u'')
    
    DBQuery().update_task_status_by_worker_assignment_id(workerId, assignmentId, Status.FINISH)
    return render_template("closepopup.html")

@task_views.errorhandler(ExperimentError)
def handleExpError(e):
    """Handle errors by sending an error page."""
    return e.error_page(request)