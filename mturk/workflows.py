import math
from mturk.manage_hit import *
from mturk.create_hit import *
from crowdtask import create_app
from crowdtask.dbquery import DBQuery
from crowdtask.enum import TaskType, WorkflowType

app=create_app()

''' 
    CLASS: UnityWorkflow
'''
class UnityWorkflow:
    def __init__(self, workflow_id, article_id=None):
        self.article_id = article_id
        self.workflow_id = workflow_id
        self.topic_map = {}
        self.relevance_map = {}
        self.link_map = {}

        self.topic_worker_list = []
        self.relevance_worker_list = []
        self.link_worker_list = []

        self.topic_rank_list = []
        self.relevance_rank_list = []
        self.link_rank_list = []

        self.topic_accuracy = []            #topic accuracy per article
        self.relevance_accuracy_all = []    #relevance accuracy per paragraph
        self.relevance_accuracy_list = []   #relevance accuracy per article
        self.link_accuracy_list = []

    def show_hit_status_by_id(self, hit_ids, stage):
        for hit_id in hit_ids.split(","):
            print "%s HIT: %s" % (stage, hit_id)
            hit = get_hit(hit_id)
            show_hit(hit)
            assignments = get_assignments(hit_id)
            print "------------------------"

    def show_all_hits_status(self):
        workflow = DBQuery().get_workflow_by_id(self.workflow_id)
        print "==================== Topic Stage ===================="
        if workflow.topic_hit_ids and workflow.topic_hit_ids != "":
            self.show_hit_status_by_id(workflow.topic_hit_ids, TaskType.TOPIC)

        print "==================== Link Stage ===================="
        if workflow.link_hit_ids and workflow.link_hit_ids != "":
            self.show_hit_status_by_id(workflow.link_hit_ids, TaskType.LINK)

        print "==================== Relevance Stage ===================="
        if workflow.relevance_hit_ids and workflow.relevance_hit_ids != "":
            self.show_hit_status_by_id(workflow.relevance_hit_ids, TaskType.RELEVANCE)

    def show_hit_status_at_topic_stage(self):
        workflow = DBQuery().get_workflow_by_id(self.workflow_id)
        self.topic_worker_list = []
        self.topic_rank_list = []
        self.topic_map = {}

        list = []
        topic_rank_list = []
        if workflow.topic_hit_ids and workflow.topic_hit_ids != "":
            topic_hits = workflow.topic_hit_ids.split(",")
            for hit_id in topic_hits:
                #print hit_id
                #hit = get_hit(hit_id)
                #show_hit(hit)
                #assignments = get_assignments(hit_id)
                #self.topic_worker_list.extend([a.WorkerId for a in assignments])

                topic_list = DBQuery().get_topics_by_hit_id(hit_id)
                
                for i in topic_list:
                    topic_sentence_key = "%s-%s" % (i[0],i[1])
                    created_user = i[2]

                    para_key = i[0]
                    if para_key in self.topic_map:
                        self.topic_map[para_key].extend([topic_sentence_key])
                    else:
                        self.topic_map[para_key] = [topic_sentence_key]
                
                    list.append(topic_sentence_key)
                    self.topic_worker_list.append(created_user)

            for par_topic in set(list):
                topic_rank_list.append((par_topic, list.count(par_topic)))

            topic_rank_list.sort(key=lambda tup: tup[1], reverse=True)
            self.topic_rank_list = topic_rank_list
            
            #print topic_rank_list
            
        else:
            print "no topic hit"

    def show_hit_status_at_relevance_stage(self, golden_topic):
        workflow = DBQuery().get_workflow_by_id(self.workflow_id)
        self.relevance_map = {}
        self.relevance_rank_list = []
        self.relevance_worker_list = []
        list = []
        relevance_rank_list = []
        if workflow.topic_hit_ids and workflow.topic_hit_ids != "":
            relevance_hits = workflow.relevance_hit_ids.split(",")
            
            for hit_id in relevance_hits:
                print hit_id
                #hit = get_hit(hit_id)
                #show_hit(hit)
                #assignments = get_assignments(hit_id)
                #self.relevance_worker_list.extend([a.WorkerId for a in assignments])

                #relevance : (article_id, paragraph_idx, relevance_word1, topic_sentence_idx, created_user)
                relevance_list = DBQuery().get_relevances_by_hit_id(hit_id)                
                for i in relevance_list:
                    items = i[2].split("-") #relevance_word: (sentence_idx, word_idx)
                    topic_sentence_key = "%d-%d-%s" % (i[0],i[1],i[3])  #[article_id]-[paragraph_idx]-[topic_sentence_idx]
                    relevance_sentence_key = "%d-%d-%s" % (i[0],i[1],items[0])  #[article_id]-[paragraph_idx]-[sentence_idx]
                    created_user = i[4]

                    if topic_sentence_key not in golden_topic[str(i[0])]:
                        continue

                    para_key = "%d-%d" % (i[0],i[1])
                    if para_key in self.relevance_map:
                        self.relevance_map[para_key].extend([(topic_sentence_key, relevance_sentence_key)])
                    else:
                        self.relevance_map[para_key] = [(topic_sentence_key, relevance_sentence_key)]

                    list.append((topic_sentence_key, relevance_sentence_key))
                    self.relevance_worker_list.append(created_user)

            for i in set(list):
                relevance_rank_list.append((i[0], i[1], list.count(i)))

            relevance_rank_list.sort(key=lambda tup: tup[2], reverse=True)
            self.relevance_rank_list = relevance_rank_list

            print relevance_rank_list
            
        else:
            print "no topic hit"


    def show_hit_status_at_link_stage(self):
        return self.link_rank_list

    def check_do_link_stage(self):
        is_tts = False
        is_ts = False
        ts_count = 0
        rank_list = self.get_topic_rank_list(weight=2)
        topic_sentence_map = {}

        if self.article_id == None and len(rank_list) > 0:
            return None
        else:
            intro_para = "%d-%d" % (self.article_id, 0)
            for topic in rank_list:
                items = topic[0].split("-")
                para_key = "%s-%s" % (items[0],items[1])
                if para_key in topic_sentence_map:
                    topic_sentence_map[para_key].extend(topic)
                else:
                    topic_sentence_map[para_key] = [topic]

            ts_count = len(topic_sentence_map.keys())

            if intro_para in topic_sentence_map:
                is_tts = True
                ts_count = ts_count - 1

            if ts_count >= 2:
                is_ts = True

        if is_tts and is_ts:
            return topic_sentence_map
        else:
            return None

    def get_topic_rank_list(self, weight=None):
        if weight:
            return filter(lambda x:x[1] >= weight, self.topic_rank_list)
        else:
            return self.topic_rank_list

    def get_topic_worker_list(self):
        return self.topic_worker_list

    def get_relevance_rank_list(self):
        return self.relevance_rank_list

    def get_relevance_worker_list(self):
        return self.relevance_worker_list

    def get_link_rank_list(self):
        return self.link_worker_list

    def get_link_worker_list(self):
        return self.link_worker_list

    def get_topic_map(self):
        return self.topic_map

    def get_relevance_map(self):
        return self.relevance_map

    def get_link_map(self):
        return self.link_map


    def get_topic_accuracy(self, golden_topic_all, weight=2):
        
        article_id = self.topic_rank_list[0][0][0].split("-")[0]
        total_topics = len(self.topic_rank_list)
        correct=0
        incorrect=0
        golden_topic = golden_topic_all[article_id]

        for item in self.topic_rank_list:
            if item[1] >= weight:
                annotation = "%s-%s" % (item[0][0],item[0][1])
            else:
                annotation = "%s-?" % (item[0][0])

            if annotation in golden_topic:
                correct = correct + 1
            else:
                incorrect = incorrect + 1

        total = correct + incorrect
        precision = correct*1.0/total
        recall = correct*1.0/len(golden_topic)
        fmeasure = 2 * (precision*recall)/(precision+recall)
        print "-------------------------"
        print "Precision: %f" % precision
        print "Recall: %f" % recall
        print "F measure: %f" % fmeasure
        self.topic_accuracy_list = (precision, recall, fmeasure, total_topics, total)

        return self.topic_accuracy_list

    def get_relevance_accuracy(self, golden_relevance_all, weight=2):
        print self.relevance_rank_list

        article_id = str(self.relevance_rank_list[0][0][0])
        total_relevance = len(self.relevance_rank_list)
        
        golden_relevance = golden_relevance_all[article_id]
        golden_relevance_map = {}
        
        for i in golden_relevance:
            items = i.split("-")
            key = "%s-%s" % (items[0], items[1])
            print key
            if key not in golden_relevance_map:
                golden_relevance_map[key] = [i]
            else:
                golden_relevance_map[key].extend([i])
                
        #by paragraph
        par_accuracy_list = []
        self.relevance_accuracy_all = []
        for par_key in self.relevance_map:
            correct=0
            incorrect=0
            relevance_list = self.relevance_map[par_key]
            if par_key in golden_relevance_map:
                golden_list = golden_relevance_map[par_key]

                relevance_list = set(relevance_list)

                print "paragraph key: %s" % par_key
                print relevance_list
                print golden_list
                print set(relevance_list)

                list = []
                for relevance in relevance_list:
                    if relevance[1] in golden_list:
                        correct = correct + 1
                    else:
                        incorrect = incorrect + 1
            
                print "correct: %d" % correct
                print "incorrect: %d" % incorrect
                total = correct + incorrect
                precision = correct*1.0/total

                recall = correct*1.0/len(golden_list)
                if precision+recall == 0:
                    fmeasure = 0
                else:
                    fmeasure = 2 * (precision*recall)/(precision+recall)

                
                par_accuracy_list.append((precision, recall, fmeasure, total_relevance, total, par_key))
                
            else:
                print "no"

            self.relevance_accuracy_all = par_accuracy_list

        p_all=0
        r_all=0
        f_all=0
        relevance_all=0
        totol_all=0
        for i in par_accuracy_list:
            p_all = p_all + i[0]
            r_all = r_all + i[1]
            f_all = f_all + i[2]

        if len(par_accuracy_list) == 0:
            a_precision = 0
            a_recall = 0
            a_fmeasure = 0
        else:
            a_precision = p_all*1.0/len(par_accuracy_list)
            a_recall = r_all*1.0/len(par_accuracy_list)
            a_fmeasure = f_all*1.0/len(par_accuracy_list)
        
        print "-------------------------"
        print "Precision: %f" % a_precision
        print "Recall: %f" % a_recall
        print "F measure: %f" % a_fmeasure

        self.relevance_accuracy_list = (a_precision, a_recall, a_fmeasure)


        return self.relevance_accuracy_list

        #for item in self.relevance_rank_list:            
        #    if item[2] >= weight:
                #annotation = "%d-%d-%s" % (item[0][0],item[0][1],item[0][2])
                #re = item[0].split("-")
                #annotation = "%d-%d-%s" % (item[0][0],item[0][1], re[0])
        #        annotation = item[1]
        #        if annotation in golden_relevance:
        #            correct = correct + 1
        #        else:
        #            incorrect = incorrect + 1


        #total = correct + incorrect
        #precision = correct*1.0/total
        #recall = correct*1.0/len(golden_relevance)
        #if precision+recall == 0:
        #    fmeasure = 0
        #else:
        #    fmeasure = 2 * (precision*recall)/(precision+recall)

        #print "-------------------------"
        #print "Precision: %f" % precision
        #print "Recall: %f" % recall
        #print "F measure: %f" % fmeasure
        #self.relevance_accuracy_list = (precision, recall, fmeasure, total_relevance, total)
        #return self.relevance_accuracy_list

''' 
    CLASS: CoherenceWorkflow
'''
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
        workflow_id = DBQuery().add_workflow(WorkflowType.UNITY, int(article_id), source=HOST, server=HOST_SERVER)
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
        
            hit_id = create_relevance_hit(article_id=article_id, paragraph_idx=paragraph_idx, 
                                            num_of_assignments=num_of_assignments, topic_sentence_idx=topic_sentence_idx)
            DBQuery().add_hit_id_to_workflow(workflow_id, task_type, hit_id)

    elif task_type == TaskType.LINK:
        if "workflow_id" not in kwargs:
            print "Please provide workflow_id"
            return 

        if "topic_list" not in kwargs:
            print "Please provide topic_list: ['4-0-1','4-1-2']"
            return

        if "thesis_statement" not in kwargs:
            print "Please provide thesis_statement: 4-0-1"
            return

        workflow_id = int(kwargs.get("workflow_id"))
        topic_list = kwargs.get("topic_list")
        thesis_statement = kwargs.get("thesis_statement")

        items = thesis_statement.split("-")
        article_id = items[0]
        paragraph_idx = items[1]
        sentence_idx = items[2]
        thesis_statement_idx = "%s-%s" % (paragraph_idx, sentence_idx)

        topic_sentence_list = []
        for i in topic_list:
            topic_items = i.split("-")
            topic_sentence_list.append("%s-%s" % (topic_items[1], topic_items[2]))

        topic_sentence_ids = "|".join(topic_sentence_list)

        hit_id = create_link_hit(article_id=article_id, thesis_statement_idx=thesis_statement_idx,
                                     topic_sentence_ids=topic_sentence_ids, num_of_assignments=num_of_assignments)

        DBQuery().add_hit_id_to_workflow(workflow_id, task_type, hit_id)

    return workflow_id

def coherence_workflow(article_id, paragraph_length, task_type, num_of_task, num_of_assignments, **kwargs):
    if task_type == TaskType.RELATION:
        workflow_id = DBQuery().add_workflow(WorkflowType.COHERENCE, int(article_id), source=HOST, server=HOST_SERVER)

        for i in range(paragraph_length):
            hit_id = create_relation_hit(article_id=article_id, paragraph_idx=str(i), num_of_assignments=num_of_assignments)
            print "hit_id: %s" % hit_id
            DBQuery().add_hit_id_to_workflow(workflow_id, task_type, hit_id)
    else:
        print "meow"

    return workflow_id


if __name__ == "__main__":
    #print "Topic Task ..."
    #article_list = ["10","11","12","13","14","15","16","17","18","19"]
#    article_list = ["20","21","22","23","24","25","26"]
#    article_list = ["24"]
#    assignment_num = 5
#    for article_id in article_list:
#        u_workflow = unity_workflow(article_id=article_id, task_type=TaskType.TOPIC, num_of_task=1, num_of_assignments=assignment_num)
#        print "workflow_id: %d" % u_workflow

    #print "Relation Task ..."
#    article_list = ["4","6","8"]
#    paragraph_length_list = [4, 5, 5]
#    assignment_num = 3
#    for i, article_id in enumerate(article_list):
#        print "artcile_id: %s, paragraph_idx: %d" % (article_id, i)
#        u_workflow = coherence_workflow(article_id=article_id, paragraph_length=paragraph_length_list[i], task_type=TaskType.RELATION, num_of_task=1, num_of_assignments=assignment_num)    
#        print "workflow_id: %d" % u_workflow
    
    #assignment_num = 3
    #workflow_article_topic_map={
    #    58: ['24-1-0','24-5-0','24-4-2','24-2-1','24-3-0','24-0-0']
    #}
#    workflow_article_topic_map={
#        37: ['5-0-1','5-2-0','5-3-1'],
#        38: ['7-0-3','7-1-0','7-3-0','7-4-0'],
#        39: ['10-0-3','10-1-0','10-2-0','10-3-3'],
#        40: ['11-0-0','11-2-0','11-3-0'],
#        41: ['12-0-1','12-1-0','12-2-0','12-3-0','12-4-0'],
#        42: ['13-0-2','13-1-0','13-2-0','13-3-0','13-5-0'],
#        43: ['14-0-1','14-1-2','14-2-2','14-3-0','14-4-0','14-5-0'],
#        44: ['15-0-0','15-1-0','15-2-0','15-3-0','15-4-0'],
#        45: ['16-0-0','16-1-0','16-2-0'],
#        46: ['17-0-0','17-1-0','17-3-0','17-4-1'],
#        47: ['18-0-0','18-1-0','18-2-0','18-3-1','18-4-0','18-5-0'],
#        48: ['19-0-0','19-4-0'],
#        49: ['20-0-0','20-2-0'],
#        50: ['21-0-1'],
#        51: ['22-0-0','22-2-0'],
#        54: ['25-0-2','25-1-0','25-4-0'],
#        55: ['26-0-3','26-1-0','26-2-0','26-3-0','26-4-0'],
#        56: ['27-0-1','27-1-0','27-2-0','27-3-0','27-4-0']
#    }
#
    #print "Relevance Task..."
    #for workflow_id in workflow_article_topic_map:
    #    topic_list = workflow_article_topic_map[workflow_id]
    #    article_id = topic_list[0].split("-")[0]
    #    u_workflow = unity_workflow(article_id=article_id, task_type=TaskType.RELEVANCE, 
    #                                num_of_task=1, num_of_assignments=assignment_num, workflow_id=workflow_id, topic_list=topic_list)
    #    print "workflow_id: %d" % u_workflow

    #print "Topic Task..."
    assignment_num = 2
    article_list = ["1","2"]
    #for article_id in article_list:
    #    u_workflow = unity_workflow(article_id=article_id, task_type=TaskType.TOPIC, num_of_task=1, num_of_assignments=assignment_num)
    #    print "workflow_id: %d" % u_workflow
    
    #get all workflows
    workflow_list=[]
    for article_id in article_list:
        article_id = int(article_id)
        workflows = DBQuery().get_workflows_by_article_id(article_id)


    print "Link Task..."
    for workflow in workflows:
        workflow_id = workflow.id
        article_id = workflow.article_id
        u = UnityWorkflow(workflow_id, article_id=article_id)
        u.show_hit_status_at_topic_stage()
        topic_rank_list = u.get_topic_rank_list(weight=2)
        topic_sentence_map = u.check_do_link_stage()

        if topic_sentence_map:
            print "do link task..."
            intro_key = "%s-0" % article_id
            tts_input = topic_sentence_map[intro_key][0][0]
            ts_input = [topic_sentence_map[key][0][0] for key in topic_sentence_map if key != intro_key]
            print "thesis statement: %s" % tts_input
            print "topic setence input: %s" % ",".join(ts_input)
            u_workflow = unity_workflow(article_id=article_id, task_type=TaskType.LINK,
                                        num_of_task=1, num_of_assignments=assignment_num,
                                        workflow_id=workflow_id, topic_list=ts_input,
                                        thesis_statement=tts_input)

            print u_workflow
            print "workflow_id: %d" % u_workflow
    
        else:
            print "Cannot do link stage"

    #print "Relevance Task..."
    #for workflow in workflows:
    #    workflow_id = workflow.id
    #    u = UnityWorkflow(workflow_id, article_id=article_id)
    #    u.show_hit_status_at_topic_stage()
    #    topic_rank_list = u.get_topic_rank_list(weight=2)
    #    topic_list = [topic[0] for topic in topic_rank_list]

    #    u_workflow = unity_workflow(article_id=article_id, task_type=TaskType.RELEVANCE,
    #                                num_of_task=1, num_of_assignments=assignment_num, workflow_id=workflow_id, topic_list=topic_list)
    #    print "workflow_id: %d" % u_workflow

    #print "all HITs status"
    #for workflow in workflows:
    #    workflow_id = workflow.id
    #    article_id = workflow.article_id
    #    u = UnityWorkflow(workflow_id, article_id=article_id)
    #    u.show_all_hits_status()

