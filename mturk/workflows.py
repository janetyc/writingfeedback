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

def unity_workflow(article_id, task_type, num_of_task, num_of_assignments, **kwargs):
    workflow_id = None
    if task_type == TaskType.TOPIC:
        workflow_id = DBQuery().add_workflow(WorkflowType.UNITY)
        print "workflow id:"
        print workflow_id
        for i in range(num_of_task):
            hit_id = create_topic_hit(article_id=article_id, num_of_assignments= num_of_assignments)

            print "hit id:"
            print hit_id
            DBQuery().add_hit_id_to_workflow(workflow_id, task_type, hit_id)
    
    elif task_type == TaskType.RELEVANCE:
        if "workflow_id" not in kwargs:
            print "Please provide workflow_id"
            return 

        workflow_id = kwargs.get("workflow_id")

        #for i in range(num_of_task):
        #    hit_id = create_relevance_hit(article_id=article_id, paragraph_idx=paragraph_idx, topic_sentence_idx=topic_sentence_idx)
    return workflow_id


def coherence_workflow():
    return

if __name__ == "__main__":
    u_workflow = unity_workflow(article_id="1", task_type=TaskType.TOPIC, num_of_task=1, num_of_assignments=2)
    print "workflow_id: %d" % u_workflow
