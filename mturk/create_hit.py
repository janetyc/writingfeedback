import os
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.qualification import Qualifications
from boto.mturk.qualification import LocaleRequirement
from boto.mturk.qualification import PercentAssignmentsApprovedRequirement

from mturk.config import mturk_config
from crowdtask.enum import TaskType

SANDBOX = mturk_config.getboolean('HIT Configuration', 'using_sandbox')
ACCESS_ID = mturk_config.get('AWS Access', 'aws_access_key_id')
SECRET_KEY = mturk_config.get('AWS Access', 'aws_secret_access_key')
HOST_SERVER = mturk_config.get('Server', 'hostname')

if SANDBOX == True:
    HOST = 'mechanicalturk.sandbox.amazonaws.com'
else:
    HOST = 'mechanicalturk.amazonaws.com'

mturk = MTurkConnection(aws_access_key_id=ACCESS_ID, aws_secret_access_key=SECRET_KEY, host=HOST)

title_set = dict({
    TaskType.TOPIC: "Find topic sentences in the paragraph",
    TaskType.RELEVANCE: "Highlight relevance ideas between two sentence",
    TaskType.RELATION: "Classify relation between two sentence",
})

description_set = dict({
    TaskType.TOPIC: "Please find the topic sentence in the article",
    TaskType.RELEVANCE: "Please highlight relevant ideas between two sentence",
    TaskType.RELATION: "Please classify relation between two sentences"
})
price_set = dict({
    TaskType.TOPIC : 0.05,
    TaskType.RELEVANCE : 0.03,
    TaskType.RELATION : 0.02,
})

keywords_set = dict({
    TaskType.TOPIC: ["annotation", "feedback", "topic", "topic sentence"],
    TaskType.RELEVANCE: ["annotation", "feedback", "relevance", "sentence relevance"],
    TaskType.RELATION: ["annotation", "feedback", "relation", "sentence relation"],
})


duration = 60 * 30
max_assignments = 1
lifetime = 60 * 60 * 24 * 7
approval_delay = 60 * 60 * 24 * 7  # auto approve
approve_requirement = 80
frame_height = 500 # the height of the iframe holding the external hit


def create_topic_hit(article_id, num_of_assignments=max_assignments):
    task_type = TaskType.TOPIC
    URL = '%s/mturk?task_type=%s&article_id=%s&using_sandbox=%s' % (HOST_SERVER, task_type, article_id, str.lower(str(SANDBOX)))
    print URL
    hit_id = create_hit(task_type, URL, num_of_assignments)

    return hit_id

def create_relevance_hit(article_id, paragraph_idx, num_of_assignmentss=max_assignments, **kwargs):
    task_type = TaskType.RELEVANCE
    URL = '%s/mturk?task_type=%s&article_id=%s&paragraph_idx=%s&using_sandbox=%s' % (HOST_SERVER, task_type, article_id, paragraph_idx, str.lower(str(SANDBOX)))

    if "topic_sentence_idx" in kwargs:
        URL += "&topic_sentence_idx=%s" % kwargs["topic_sentence_idx"]

    print URL
    hit_id = create_hit(task_type, URL, num_of_assignments)

    return hit_id

def create_relation_hit(article_id, paragraph_idx, num_of_assignments=max_assignments, **kwargs):
    task_type = TaskType.RELATION
    URL = '%s/mturk?task_type=%s&article_id=%s&paragraph_idx=%s&using_sandbox=%s' % (HOST_SERVER, task_type, article_id, paragraph_idx, str.lower(str(SANDBOX)))
    print URL

    hit_id = create_hit(task_type, URL, num_of_assignments)
    return hit_id

def create_hit(task_type, URL, num_of_assignments):
    title = title_set[task_type]
    description = description_set[task_type]
    keywords = keywords_set[task_type]
    reward = price_set[task_type]
    
    print mturk.get_account_balance()

    # Qualification
    qualifications = Qualifications()
    qualifications.add(PercentAssignmentsApprovedRequirement("GreaterThanOrEqualTo", approve_requirement))
    #qualifications.add(LocaleRequirement("EqualTo", "US"))
    #qualifications.add(LocaleRequirement("In", ['US', 'GB', 'IN'], required_to_preview=True))
    questionform = ExternalQuestion(URL, frame_height)

    # create HIT
    create_hit_result = mturk.create_hit(
        title=title,
        description=description,
        keywords=keywords,
        question=questionform,
        reward=reward,
        qualifications=qualifications,

        duration=duration,
        max_assignments=num_of_assignments,
        lifetime=lifetime,
        approval_delay=approval_delay
        #response_groups = ( 'Minimal', 'HITDetail' ), # I don't know what response groups are
    )

    HIT = create_hit_result[0]
    assert create_hit_result.status

    print '[create_hit( %s, $%s ): %s]' % (URL, reward, HIT.HITId)
    print HIT.HITId
    return HIT.HITId


if __name__ == "__main__":
    print "test create hit"
    #topic_hit = create_topic_hit(article_id="1")
    #relevance_hit = create_relevance_hit(article_id="2", paragraph_idx="2", topic_sentence_idx="1")
    #relation_hit = create_relation_hit(article_id="3", paragraph_idx="2")
