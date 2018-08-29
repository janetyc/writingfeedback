import re
import math
from mturk.manage_hit import *
from mturk.create_hit import *

from crowdtask.dbquery import DBQuery
from mturk.workflows import UnityWorkflow

class GoldenStandard:
    def __init__(self):
        self.standard_topic_relevance = {}
        self.article_map = {}
        self.expert_map = {}
        self.topic_rank = {}
        self.topic_standard = {}
        self.relevance_rank = {}
        self.relevance_standard = {}

    def load_golden_from_file(self, standard_topic_relevance):
        self.standard_topic_relevance = standard_topic_relevance

    def load_golden_from_db(self, article_id_list):
        all_goldens = []
        for article_id in article_id_list:
            article_id = str(article_id)
            if article_id not in self.article_map:
                self.article_map[article_id] = {
                    "topic": [],
                    "relevance": []
                }

            golden_structures = DBQuery().get_golden_structures_by_article_id(article_id)
            for golden in golden_structures:
                topic_map = {}
                topic_list = []
                for topic in golden.topic.split("|"):
                    topic_items = topic.split("-")
                    topic_list.append("%s-%s" % (article_id, topic))
                    topic_key = "%s-%s" % (article_id, topic_items[0])
                    #if topic_key not in topic_map:
                    #    topic_map[topic_key] = []
                    #topic_map[topic_key].append(topic_items[1])
                    topic_map[topic_key] = topic_items[1]

                relevance_list = []
                for relevance in golden.relevance.split("|"):
                    relevance_items=relevance.split("-")
                    relevance = "%s-%s-%s-%s" % (article_id, relevance_items[0], relevance_items[1], relevance_items[2])
                    topic_relevance_key = "%s-%s" % (article_id, relevance_items[0])
                    if topic_relevance_key in topic_map:
                        topic_sentence_idx = topic_map[topic_relevance_key]
                        relevance_list.append((relevance, topic_sentence_idx))
                    

                self.article_map[article_id]["topic"].extend(topic_list)
                self.article_map[article_id]["relevance"].extend(relevance_list)

                print topic_map
        
        print self.article_map
        print "finished!"

    #old function: aggregate relevance
    def aggregate_result(self):
        print "do aggregation"
        for article in standard_topic_relevance:
            items = article.split("-")
            article_id = items[0]
            expert_id = items[1]

            if article_id not in self.article_map:
                self.article_map[article_id] = {
                    "topic": [],
                    "relevance": []
                }

            relevance_collection = []
            for i, task_codes in enumerate(standard_topic_relevance[article]):
                for task_code in task_codes.split(","):
                    if task_code == "":
                        print "no topic sentence"
                        continue

                    task = DBQuery().get_task_by_code(task_code)
                    if not task:
                        print "skip - %s" % task_code
                        continue

                    relevance_list = []
                    if task.answer == "":
                        print "no relevance - %s" % task_code                      
                        
                    else:
                        for task_id in task.answer.split("|"):
                            relevance_list = DBQuery().get_relevance_by_id(task_id)
                            #print relevance_list
                            list = [("%d-%d-%s" % (relevance[0],relevance[1],relevance[2]), relevance[3]) for relevance in relevance_list]
                            self.article_map[article_id]["relevance"].extend(list)

        print self.article_map
        print "finished!"

    def update_topic(self, annotator):
        for article_id in annotator:
            topic_list = annotator[article_id]

            list = []
            for i, topic in enumerate(topic_list):
                key = "%s-%d-%s" % (article_id,i,topic)
                list.append(key)

            self.article_map[article_id]["topic"].extend(list)


    def get_article_map(self):
        return self.article_map

    def get_topic_rank(self):
        for article_id in self.article_map:
            topics = set(self.article_map[article_id]["topic"])
            list = []
            standard_list = []
            for i in topics:
                count = self.article_map[article_id]["topic"].count(i) 
                list.append((count, i))
                
                if count >= 2:
                    standard_list.append(i)
                
            list = sorted(list, reverse=True)
            self.topic_rank[article_id] = list
            self.topic_standard[article_id] = standard_list


        return self.topic_rank


    def get_topic_standard(self):
        if not self.topic_standard:
            self.get_topic_rank()

        return self.topic_standard

    def get_relevance_rank(self):
        for article_id in self.article_map:
            relevances = set(self.article_map[article_id]["relevance"])
            list = []
            standard_list = []
            new_relevances = []
            for i in relevances:
                items = i[0].split("-")
                topic_sentence_key = "%s-%s-%s" % (items[0], items[1], i[1])
                relevance_sentence_key = "%s-%s-%s" % (items[0], items[1], items[2])
                if topic_sentence_key not in self.topic_standard[article_id]:
                    continue

                new_relevances.append(relevance_sentence_key)

            for i in set(new_relevances):
                count = new_relevances.count(i) 
                list.append((count, i))
                
                if count >= 2:
                    standard_list.append(i)
                
            list = sorted(list, reverse=True)
            self.relevance_rank[article_id] = list
            self.relevance_standard[article_id] = standard_list

        return self.relevance_rank

    def get_relevance_standard(self):
        if not self.relevance_standard:
            self.get_relevance_rank()

        return self.relevance_standard


def cal_consistency(rank_list):
    par_map = {}
    for item in rank_list:
        print item
        weight = item[1]
        par_info = item[0].split('-')
        par_key = "%s-%s" % (par_info[0], par_info[1])

        if par_key in par_map:
            par_map[par_key].extend([item])
        else:
            par_map[par_key] = [item]

    entropy_list = []
    for par in par_map:
        list = par_map[par]
        print "---"
        print list
        total_value = sum(zip(*list)[1])
        p_list = [i[1]*1.0/total_value for i in list]
        log_items = [p*math.log(p,2) for p in p_list]
        entropy = sum(log_items)*-1
        entropy_list.append( (par, entropy) )

    
    entropy_list = sorted(entropy_list, key=lambda x: x[1], reverse=True)
    return entropy_list


if __name__ == "__main__":
    print "--------- Calculate Results ---------"
    print "------- Read Golden Standard --------"
    article_id_list = [41,34,30,40,31,46,38,43,35,44,29,36,42,32,33]
    #article_id_list = [30]
    golden = GoldenStandard()
    golden.load_golden_from_db(article_id_list)
    
    golden_topic_rank = golden.get_topic_rank()
    topic_standard = golden.get_topic_standard()

    golden_relevance_rank = golden.get_relevance_rank()
    relevance_standard = golden.get_relevance_standard()

    print "--------------------------------------"
    golden_topic = topic_standard
    golden_relevance = relevance_standard

    print golden_topic
    print golden_relevance

    all_topics = []
    all_relevances = []
    all_irrelevances = []

    avg_topic_entropy=[]
    avg_relevance_entropy=[]
    entropy_all_topic = []
    entropy_all_relevance = []
    global_topic_map = {}
    global_relevance_map = {}
    
    topic_accuracy_list = []
    relevance_accuracy_list = []
    irrelevance_accuracy_list = []

    topic_worker_list = []
    relevance_worker_list = []


    for i in [75,67,63,73,64,80,71,77,68,78,62,69,76,65,66]:
    #for i in [65]:
        print "workflow: %d" % i
        u = UnityWorkflow(i)
        print u.article_id
        print "*****************"

        #topic
        u.show_hit_status_at_topic_stage()
        topic_rank_list = u.get_topic_rank_list()      

        #worker
        topic_workers = u.get_topic_worker_list()
        topic_worker_list.extend(topic_workers)

        topic_map = u.get_topic_map()
        global_topic_map[i] = topic_map

        #accuracy
        accuracy = u.get_topic_accuracy(golden_topic_all=golden_topic, weight=3)
        topic_accuracy_list.append((i, accuracy))
        all_topics.extend(topic_rank_list)
        
        #relevance
        print "*****************************************"
        u.show_hit_status_at_relevance_stage(golden_topic)
        relevance_rank_list = u.get_relevance_rank_list()

        print "*****************************************"

        #worker
        relevance_workers = u.get_relevance_worker_list()
        relevance_worker_list.extend(relevance_workers)

        relevance_map = u.get_relevance_map()
        global_relevance_map[i] = relevance_map
        
        accuracy = u.get_relevance_accuracy(golden_relevance_all=golden_relevance, weight=1)
        relevance_accuracy_list.append((i, accuracy))
        all_relevances.extend(relevance_rank_list)

        #irrelevance
        irrelevance_accuracy = u.get_irrelevance_accuracy(golden_relevance_all=golden_relevance, golden_topic_all=golden_topic)
        irrelevance_accuracy_list.append((i, irrelevance_accuracy))
        irrelevance_list = u.get_irrelevance_list()
        all_irrelevances.extend(irrelevance_list)

        #topic
        temp_topic = [ ("%s-%s"%(i[0][0],i[0][1]),i[1]) for i in topic_rank_list]
        topic_entropy = cal_consistency(temp_topic)
        entropy_all_topic.extend(topic_entropy)
        if len(topic_entropy):
            avg_topic_entropy.append( sum([i[1] for i in topic_entropy])/len(topic_entropy) )
        else:
            avg_topic_entropy.append(0)

        temp_relevance = [ (i[1], i[2]) for i in relevance_rank_list]
        relevance_entropy = cal_consistency(temp_relevance)
        entropy_all_relevance.extend(relevance_entropy)
        if len(relevance_entropy):
            avg_relevance_entropy.append( sum([i[1] for i in relevance_entropy])/len(relevance_entropy))
        else:
            avg_relevance_entropy.append(0)
    
    print " ---------------- Results ----------------------------------"
    print "topic stage"
    print "workers: %d" % len(topic_worker_list)
    print "distrinct workers: %d" % len(set(topic_worker_list))

    print "relevance stage"
    print "workers: %d" % len(relevance_worker_list)
    print "distrinct workers: %d" % len(set(relevance_worker_list))
    
    print topic_accuracy_list
    print relevance_accuracy_list
    print irrelevance_accuracy_list

    print "---- topic golden -----"
    print golden_topic_rank

    print "---- relevance golden -----"
    print golden_relevance_rank

    print "---------- Golden ------------------------------------------"
    print golden_topic
    print golden_relevance

    print "------------ Topic & Relevance Ranked List ------------------------------"
    print global_topic_map
    print global_relevance_map

    print "------------- Topic Entropy -------------------"
    entropy_all_topic.sort(key=lambda x: x[1], reverse=True)
    print entropy_all_topic

    print "------------- Relevance Entropy -------------------"
    entropy_all_relevance.sort(key=lambda x: x[1], reverse=True)
    print entropy_all_relevance

    avg_golden_topic=[]
    avg_golden_relevance=[]
    golden_topic_entropy=[]
    golden_relevance_entropy=[]
    for article_id in golden_topic_rank:
        temp = golden_topic_rank[article_id]
        temp_list = [(i[1],i[0]) for i in temp]
        g_topic_entropy = cal_consistency(temp_list)
        golden_topic_entropy.extend(g_topic_entropy)
        if len(g_topic_entropy):
            avg_golden_topic.append( sum([i[1] for i in g_topic_entropy])/len(g_topic_entropy) )
        else:
            avg_golden_topic.append(0)

    for article_id in golden_relevance_rank:
        temp = golden_relevance_rank[article_id]
        temp_list = [(i[1],i[0]) for i in temp]
        g_relevance_entropy = cal_consistency(temp_list)
        golden_relevance_entropy.extend(g_relevance_entropy)
        
        if len(g_relevance_entropy):
            avg_golden_relevance.append( sum([i[1] for i in g_relevance_entropy])/len(g_relevance_entropy) )
        else:
            avg_golden_relevance.append(0)

    print "------------- Golden Topic Entropy -------------------"
    golden_topic_entropy = sorted( golden_topic_entropy, key=lambda x: x[1], reverse=True)
    print golden_topic_entropy
    
    print "------------- Golden Relevance Entropy -------------------"
    golden_relevance_entropy = sorted( golden_relevance_entropy, key=lambda x: x[1], reverse=True)
    print golden_relevance_entropy

    print "-------------------- AVG Entroy ---------------"
    print "--- topic ---"
    print avg_topic_entropy
    print "--- relevance ---" 
    print avg_relevance_entropy
    print "--- golden topic ---"
    print avg_golden_topic
    print "--- golden relevance ---"
    print avg_golden_relevance

    print "--------------------------------------------------"
    print "topic size: %d" % len(all_topics)
    print "relevance size: %d" % len(all_relevances)
        
