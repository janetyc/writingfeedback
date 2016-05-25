from mturk.manage_hit import *
from mturk.create_hit import *
from crowdtask import create_app
from crowdtask.dbquery import DBQuery
from crowdtask.enum import TaskType, WorkflowType
app=create_app()

class UnityWorkflow:

    def __init__(self, workflow_id):
        self.workflow_id = workflow_id
        self.topic_map = {}
        
    def show_hit_status_at_topic_stage(self):
        workflow = DBQuery().get_workflow_by_id(self.workflow_id)
        if workflow.topic_hit_ids != "":
            topic_hits = workflow.topic_hit_ids.split(",")
            for hit_id in topic_hits:
                print hit_id
                hit = get_hit(hit_id)
                show_hit(hit)
                assignments = get_assignments(hit_id)

                topic_rank_list = []
                topic_list = DBQuery().get_topics_by_hit_id(hit_id)
                for par_topic in set(topic_list):
                    topic_rank_list.append((par_topic, topic_list.count(par_topic)))

                topic_rank_list.sort(key=lambda tup: tup[1], reverse=True)
                print topic_rank_list
            
        else:
            print "no topic hit"


class CoherenceWorkflow:
    def __init__(self, workflow_id):
        self.workflow_id = workflow_id
        self.relation_map = {}

    def show_hit_status(self):
        workflow = DBQuery().get_workflow_by_id(self.workflow_id)
        print workflow.relation_hit_ids
        if workflow.relation_hit_ids != "":
            relation_hits = workflow.relation_hit_ids.split(",")
            for hit_id in relation_hits:
                print hit_id
                hit = get_hit(hit_id)
                show_hit(hit)
                assignments = get_assignments(hit_id)



def unity_workflow(article_id, task_type, num_of_task, num_of_assignments, **kwargs):
    workflow_id = None
    if task_type == TaskType.TOPIC:
        workflow_id = DBQuery().add_workflow(WorkflowType.UNITY)
        print "workflow id:"
        print workflow_id
        for i in range(num_of_task):
            hit_id = create_topic_hit(article_id=article_id, num_of_assignments=num_of_assignments)

            print "hit id:"
            print hit_id
            DBQuery().add_hit_id_to_workflow(workflow_id, task_type, hit_id)
    
    elif task_type == TaskType.RELEVANCE:
        if "workflow_id" not in kwargs:
            print "Please provide workflow_id"
            return 

        if "topic_list" not in kwargs:
            print "Please provide topic_list: ['4-0-1','4-1-2']"
            return 

        workflow_id = int(kwargs.get("workflow_id"))
        topic_list = kwargs.get("topic_list")

        for topic in topic_list:
            items = topic.split("-")
            article_id = items[0]
            paragraph_idx = items[1]
            topic_sentence_idx = items[2]
        
            hit_id = create_relevance_hit(article_id=article_id, paragraph_idx=paragraph_idx, topic_sentence_idx=topic_sentence_idx)
            DBQuery().add_hit_id_to_workflow(workflow_id, task_type, hit_id)


    return workflow_id

def coherence_workflow(article_id, paragraph_length, task_type, num_of_task, num_of_assignments, **kwargs):
    if task_type == TaskType.RELATION:
        workflow_id = DBQuery().add_workflow(WorkflowType.COHERENCE)

        for i in range(paragraph_length):
            hit_id = create_relation_hit(article_id=article_id, paragraph_idx=str(i), num_of_assignments=num_of_assignments)
            print "hit_id: %s" % hit_id
            DBQuery().add_hit_id_to_workflow(workflow_id, task_type, hit_id)
    else:
        print "meow"

    return workflow_id

if __name__ == "__main__":
#    article_list = ["4","6","8"]
#    assignment_num = 5
#    for article_id in article_list:
#        u_workflow = unity_workflow(article_id=article_id, task_type=TaskType.TOPIC, num_of_task=1, num_of_assignments=assignment_num)
#        print "workflow_id: %d" % u_workflow

#    print "Relation Task ..."
#    article_list = ["4","6","8"]
#    paragraph_length_list = [4, 5, 5]
#    assignment_num = 3
#    for i, article_id in enumerate(article_list):
#        print "artcile_id: %s, paragraph_idx: %d" % (article_id, i)
#        u_workflow = coherence_workflow(article_id=article_id, paragraph_length=paragraph_length_list[i], task_type=TaskType.RELATION, num_of_task=1, num_of_assignments=assignment_num)    
#        print "workflow_id: %d" % u_workflow
    assignment_num = 3
    print "Relevance Task..."
    workflow_list = [9,10,11]
    article_topic_list = [['4-0-2','4-1-0'],['6-0-0', '6-1-0', '6-2-0', '6-3-0', '6-4-0'],['8-0-3','8-1-0','8-2-0','8-3-0','8-4-0']]
    for i, workflow_id in enumerate(workflow_list):
        topic_list = article_topic_list[i]
        article_id = topic_list[0].split("-")[0]
        u_workflow = unity_workflow(article_id=article_id, task_type=TaskType.RELEVANCE, 
                                    num_of_task=1, num_of_assignments=assignment_num, workflow_id=workflow_id, topic_list=topic_list)
        
        print "workflow_id: %d" % u_workflow



