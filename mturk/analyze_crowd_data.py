import re
import csv
import json
from mturk.manage_hit import *
from mturk.create_hit import *

from crowdtask.dbquery import DBQuery
from mturk.workflows import UnityWorkflow

def save_to_json(workflow_id, data):
    with open('crowd_data/workflow_%d.json' % workflow_id, 'w') as f:
        json.dump(data, f, ensure_ascii=False)

    #print "save workflow #%d data" % workflow_id

def read_crowd_data_from_json(workflow_id):
    print "read workflow #%d data" % workflow_id
    with open('crowd_data/workflow_%d.json' % workflow_id) as f:
        data = json.loads(f.read())
    return data

def read_golden_data(article_id):
    print "read golden data (article_id): %d" % article_id
    with open('expert_data/article_%d.json' % article_id) as f:
        data = json.loads(f.read())

    results = {}
    golden_data = data["data"]
    for golden_id in golden_data:
        results[golden_data[golden_id]["created_user"]] = {
            "topic": golden_data[golden_id]["golden_topics"],
            "relevance": golden_data[golden_id]["golden_relevances"],
            "irrelevance": golden_data[golden_id]["golden_irrelevances"]
        }
    return results

def generate_golden_topic_annotation(article_id):
    return []

def generate_topic_sentence():
    results = []
    return results

def generate_relevant_sentence():
    results = []
    return results

def generate_irrelevant_sentence():
    results = []
    return results

def cal_hit_count(workflow_id_list):
    all_topic_hits =[]
    all_relevance_hits=[]
    for i, workflow_id in enumerate(workflow_id_list):
        workflow = DBQuery().get_workflow_by_id(workflow_id)
        if workflow.topic_hit_ids and workflow.topic_hit_ids != "":
            topic_hits = workflow.topic_hit_ids.split(",")
            all_topic_hits.extend(topic_hits)

        if workflow.relevance_hit_ids and workflow.relevance_hit_ids != "":
            relevance_hits = workflow.relevance_hit_ids.split(",")
            all_relevance_hits.extend(relevance_hits)


    print "Topic HITs count: %d (5 assignments)" % len(all_topic_hits)
    print "Relevance HITs count: %d (5 assignments)" % len(all_relevance_hits)

def cal_accuracy(golden, crowd_ans, output):
    #print "cal"
    print crowd_ans
    print golden
    TP=0
    FP=0
    for g in golden:
        output[g] = 0
    for a in crowd_ans:
        output[a[1]] = 1
        if golden[a[1]]:
            TP=TP+1
        else:
            FP=FP+1

    if TP+FP:
        precision = TP*1.0/(TP+FP)
    else:
        precision = 0.0

    if golden.values().count(1):
        recall = TP*1.0/golden.values().count(1)
    else:
        recall = 1.0

    if precision+recall: 
        fscore = 2*(precision*recall)/(precision+recall)
    else:
        fscore = 0.0

    return (precision, recall, fscore, len(crowd_ans), golden.values().count(1), TP, FP)

def print_results(article_order, results):
    TP = 0
    FP = 0
    total_golden = 0
    for i,r in enumerate(results):
        #print "%d: %f\t%f\t%f\t(%d,%d,%d,%d)" % (article_order[i],r[0],r[1],r[2],r[3],r[4],r[5],r[6])
        TP = TP+r[5]
        FP = FP+r[6]
        total_golden = total_golden+r[4]

    precision = 1.0*TP/(TP+FP)
    recall = 1.0*TP/total_golden
    fscore = 2*(precision*recall)/(precision+recall)
    #print "(TP, TP+FP, total golden): %d,%d,%d" % (TP, (TP+FP), total_golden)
    print "average: %f\t%f\t%f" % (precision, recall, fscore)

def print_annotation(datatype, annotator, data_map):
    keys = []
    data = []
    for article in data_map:
        keys.extend(data_map[article].keys())
        data.extend(data_map[article].values())

    data = [str(d) for d in data]
    result = ""
    result = "\t".join(keys)
    result = result + "\n"
    result = result + "\t".join(data)
    
    print "type: %s" % datatype
    print "annotator: %s" % annotator
    print "size: %d" % len(data)
    print result

    with open("csv/%s-%s.csv" % (datatype, annotator), "w") as fp:
        writer = csv.writer(fp, delimiter=',')
        writer.writerows([data])

    print keys
    print "write %s-%s.csv" % (datatype, annotator)
    
    with open("csv/keys.csv", "w") as fp:
        writer = csv.writer(fp, delimiter=',')
        writer.writerows([keys])

if __name__ == "__main__":
    article_id_list = [41,34,30,40,31,46,38,43,35,44,29,36,42,32,33]
    workflow_id_list = [75,67,63,73,64,80,71,77,68,78,62,69,76,65,66]
    #article_id_list=[33]
    #workflow_id_list=[66]

    article_sentences_map = {}
    article_words_map = {}
    golden_data = {}
    for article_id in article_id_list:
        golden_data[article_id] = read_golden_data(article_id)
        article = DBQuery().get_article_by_id(article_id)
        all_sentences = []
        all_words = []
        for paragraph_idx, paragraph in enumerate(article.content.split("<BR>")):
            if paragraph:
                sentence_list = re.split(r'(?<=[^A-Z].[.?]) +(?=[A-Z])', paragraph)
                for sentence_idx, sentence in enumerate(sentence_list):
                    sentence_key = "%d-%d-%d" % (article_id, paragraph_idx, sentence_idx)
                    sentence = sentence.strip()
                    word_list = sentence.split(" ")
                    for word_idx, word in enumerate(word_list):
                        word_key = "%s-%d" % (sentence_key, word_idx)
                        all_words.append(word_key)

                    all_sentences.append(sentence_key)

        article_sentences_map[article_id] = all_sentences
        article_words_map[article_id] = all_words

    data_map = {}
    topic_map = {}
    relevance_map = {}
    relevant_keywords_map = {}
    for i, workflow_id in enumerate(workflow_id_list):
        #save data to json
        #u = UnityWorkflow(workflow_id, article_id_list[i])
        #data = u.save_crowd_data_by_workflow_id()
        #save_to_json(workflow_id, data)
        
        article_id = article_id_list[i]
        data = read_crowd_data_from_json(workflow_id)
        data_map[article_id] = data
        topic_map[article_id] = []
        relevance_map[article_id] = []
        relevant_keywords_map[article_id] = []
        topics=[]
        relevances=[]
        relevant_keywords=[]
        for j in data["topic"].values():
            topics.extend(j)

        for j in set(topics):
            topic_map[article_id].append((topics.count(j),j))

        topic_map[article_id] = sorted(topic_map[article_id], reverse=True)

        for j in data["relevance"]:
            r_list = data["relevance"][j]
            r_sentence_list = []
            for r in r_list:
                elem = r[0].split("-")
                r_key = "%s-%s-%s" % (elem[0],elem[1],elem[2])
                if r_key not in r_sentence_list:
                    r_sentence_list.append(r_key)

            relevances.extend(r_sentence_list)
            relevant_keywords.extend(j)

        #for j in data["relevance"].values():
        #    for k in j:
        #        r_items = k[0].split("-")
        #        relevances.append("%s-%s-%s" % (r_items[0],r_items[1],r_items[2]))
        #
        #
        #    relevant_keywords.extend(k[0])

        for j in set(relevances):
            relevance_map[article_id].append((relevances.count(j),j)) 


        for j in set(relevant_keywords):
            relevant_keywords_map[article_id].append((relevant_keywords.count(j),j))

        relevance_map[article_id] = sorted(relevance_map[article_id], reverse=True)
        relevant_keywords_map[article_id] = sorted(relevant_keywords_map[article_id], reverse=True)


    #for article_id in data_map:
    #    print "article_id: %d" % article_id
    #    print "topic: (%d workers)" % len(data_map[article_id]["topic"])
    #    print data_map[article_id]["topic"]
    #    print "relevance: (%d workers)" % len(data_map[article_id]["relevance"])
    #    print data_map[article_id]["relevance"]
    #    print "---------------"
    #    print golden_data[article_id]
    #    print topic_map[article_id]
    #print "finished!"

    #topic sentence
    topic_idx_list = []
    topic_annotations = {}
    topic_annotations["expert1"] = {}
    topic_annotations["expert2"] = {}
    topic_annotations["expert-intersect"] = {}
    topic_annotations["expert-union"] = {}
    topic_annotations["crowd1"] = {}
    topic_annotations["crowd2"] = {}
    topic_annotations["crowd-intersect"] = {}
    topic_annotations["crowd-union"] = {}

    relevance_annotations = {}
    relevance_annotations["expert1"] = {}
    relevance_annotations["expert2"] = {}
    relevance_annotations["expert-intersect"] = {}
    relevance_annotations["expert-union"] = {}
    relevance_annotations["crowd1"] = {}
    relevance_annotations["crowd2"] = {}
    relevance_annotations["crowd-intersect"] = {}
    relevance_annotations["crowd-union"] = {}

    irrelevance_annotations = {}
    irrelevance_annotations["expert1"] = {}
    irrelevance_annotations["expert2"] = {}
    irrelevance_annotations["expert-intersect"] = {}
    irrelevance_annotations["expert-union"] = {}
    irrelevance_annotations["crowd1"] = {}
    irrelevance_annotations["crowd2"] = {}
    irrelevance_annotations["crowd-intersect"] = {}
    irrelevance_annotations["crowd-union"] = {}

    #golden x 2
    for article_id in article_sentences_map:
        topic_annotations["expert1"][article_id] = {}
        topic_annotations["expert2"][article_id] = {}
        relevance_annotations["expert1"][article_id] = {}
        relevance_annotations["expert2"][article_id] = {}
        irrelevance_annotations["expert1"][article_id] = {}
        irrelevance_annotations["expert2"][article_id] = {}

        article_sentences = article_sentences_map[article_id]
        
        golden_r = {}
        for expert in ["expert1","expert2"]:
            r_list = golden_data[article_id][expert]["relevance"]
            golden_r_list = []
            for r in r_list:
                items = r.split("-")
                r_key = "%s-%s-%s" % (items[0],items[1],items[2])
                golden_r_list.append(r_key)
            
            golden_r[expert] = golden_r_list


        for sentence in article_sentences:
            for subject in ["expert1", "expert2"]:
                #topic
                if sentence in golden_data[article_id][subject]["topic"]:
                    ans = 1
                else:
                    ans = 0
                
                topic_annotations[subject][article_id][sentence] = ans

                #relevance
                if sentence in golden_r[subject]:
                    ans = 1
                else:
                    ans = 0

                relevance_annotations[subject][article_id][sentence] = ans

                if topic_annotations[subject][article_id][sentence]|relevance_annotations[subject][article_id][sentence]:
                    irrelevance_annotations[subject][article_id][sentence] = 0
                else:
                    irrelevance_annotations[subject][article_id][sentence] = 1

            topic_idx_list.append(sentence)
                
    #golden intersect, union
    for article_id in article_sentences_map:
        article_sentences = article_sentences_map[article_id]
        topic_annotations["expert-intersect"][article_id] = {}
        topic_annotations["expert-union"][article_id] = {}

        relevance_annotations["expert-intersect"][article_id] = {}
        relevance_annotations["expert-union"][article_id] = {}

        irrelevance_annotations["expert-intersect"][article_id] = {}
        irrelevance_annotations["expert-union"][article_id] = {}
        for sentence in article_sentences:
            topic_annotations["expert-intersect"][article_id][sentence] = topic_annotations["expert1"][article_id][sentence]&topic_annotations["expert2"][article_id][sentence]
            topic_annotations["expert-union"][article_id][sentence] = topic_annotations["expert1"][article_id][sentence]|topic_annotations["expert2"][article_id][sentence]

            relevance_annotations["expert-intersect"][article_id][sentence] = relevance_annotations["expert1"][article_id][sentence]&relevance_annotations["expert2"][article_id][sentence]
            relevance_annotations["expert-union"][article_id][sentence] = relevance_annotations["expert1"][article_id][sentence]|relevance_annotations["expert2"][article_id][sentence]

            irrelevance_annotations["expert-intersect"][article_id][sentence] = irrelevance_annotations["expert1"][article_id][sentence]&irrelevance_annotations["expert2"][article_id][sentence]
            irrelevance_annotations["expert-union"][article_id][sentence] = irrelevance_annotations["expert1"][article_id][sentence]|irrelevance_annotations["expert2"][article_id][sentence]


    
    topic_accuracy_list_intersect=[]
    topic_accuracy_list_union=[]
    topic_accuracy_list_expert1=[]
    topic_accuracy_list_expert2=[]

    relevance_accuracy_list_intersect=[]
    relevance_accuracy_list_union=[]
    relevance_accuracy_list_expert1=[]
    relevance_accuracy_list_expert2=[]

    irrelevance_accuracy_list_intersect=[]
    irrelevance_accuracy_list_union=[]
    irrelevance_accuracy_list_expert1=[]
    irrelevance_accuracy_list_expert2=[]
    topic_weight = 2
    relevance_weight = 3
    article_order =[] 
    for article_id in article_sentences_map:
        article_order.append(article_id)
        crowd_topic_ans = filter(lambda x:x[0] >= topic_weight, topic_map[article_id])
        topic_annotations["crowd-intersect"][article_id] = {}
        acc = cal_accuracy(topic_annotations["expert-intersect"][article_id], crowd_topic_ans, topic_annotations["crowd-intersect"][article_id])
        topic_accuracy_list_intersect.append(acc)

        topic_annotations["crowd-union"][article_id] = {}
        acc = cal_accuracy(topic_annotations["expert-union"][article_id], crowd_topic_ans, topic_annotations["crowd-union"][article_id])
        topic_accuracy_list_union.append(acc)

        topic_annotations["crowd1"][article_id] = {}
        acc = cal_accuracy(topic_annotations["expert1"][article_id], crowd_topic_ans, topic_annotations["crowd1"][article_id])
        topic_accuracy_list_expert1.append(acc)        

        topic_annotations["crowd2"][article_id] = {}
        acc = cal_accuracy(topic_annotations["expert2"][article_id], crowd_topic_ans, topic_annotations["crowd2"][article_id])
        topic_accuracy_list_expert2.append(acc)

        #--------------------------------------------------------------------
        crowd_relevance_ans = filter(lambda x:x[0] >= relevance_weight, relevance_map[article_id])
        relevance_annotations["crowd-intersect"][article_id] = {}
        acc = cal_accuracy(relevance_annotations["expert-intersect"][article_id], crowd_relevance_ans, relevance_annotations["crowd-intersect"][article_id])
        relevance_accuracy_list_intersect.append(acc)

        relevance_annotations["crowd-union"][article_id] = {}
        acc = cal_accuracy(relevance_annotations["expert-union"][article_id], crowd_relevance_ans, relevance_annotations["crowd-union"][article_id])
        relevance_accuracy_list_union.append(acc)

        relevance_annotations["crowd1"][article_id] = {}
        acc = cal_accuracy(relevance_annotations["expert1"][article_id], crowd_relevance_ans, relevance_annotations["crowd1"][article_id])
        relevance_accuracy_list_expert1.append(acc)        

        relevance_annotations["crowd2"][article_id] = {}
        acc = cal_accuracy(relevance_annotations["expert2"][article_id], crowd_relevance_ans, relevance_annotations["crowd2"][article_id])
        relevance_accuracy_list_expert2.append(acc)


        #--------------------------------------------------------------------
        crowd_high_relevance_ans = [i[1] for i in (crowd_topic_ans + crowd_relevance_ans)]
        temp_ans = set(article_sentences_map[article_id])-set(crowd_high_relevance_ans)
        crowd_irrelevance_ans = [(2,a) for a in temp_ans]
        irrelevance_annotations["crowd-intersect"][article_id] = {}
        acc = cal_accuracy(irrelevance_annotations["expert-intersect"][article_id], crowd_irrelevance_ans, irrelevance_annotations["crowd-intersect"][article_id])
        irrelevance_accuracy_list_intersect.append(acc)

        irrelevance_annotations["crowd-union"][article_id] = {}
        acc = cal_accuracy(irrelevance_annotations["expert-union"][article_id], crowd_irrelevance_ans, irrelevance_annotations["crowd-union"][article_id])
        irrelevance_accuracy_list_union.append(acc)

        irrelevance_annotations["crowd1"][article_id] = {}
        acc = cal_accuracy(irrelevance_annotations["expert1"][article_id], crowd_irrelevance_ans, irrelevance_annotations["crowd1"][article_id])
        irrelevance_accuracy_list_expert1.append(acc)        

        irrelevance_annotations["crowd2"][article_id] = {}
        acc = cal_accuracy(irrelevance_annotations["expert2"][article_id], crowd_irrelevance_ans, irrelevance_annotations["crowd2"][article_id])
        irrelevance_accuracy_list_expert2.append(acc)


    print "------------------------------------"
    print "Topic threshold: %d" % topic_weight
    print "Relevance threshold: %d" % relevance_weight
    print "-----topic intersect-----"
    print_results(article_order,topic_accuracy_list_intersect)
    
    print "-----topic union-----"
    print_results(article_order,topic_accuracy_list_union)

    print "-----topic expert1-----"
    print_results(article_order,topic_accuracy_list_expert1)

    print "-----topic expert2-----"
    print_results(article_order,topic_accuracy_list_expert2)

    print "------------------------------------"
    print "------------------------------------"
    print "-----relevance intersect-----"
    print_results(article_order,relevance_accuracy_list_intersect)
    
    print "-----relevance union-----"
    print_results(article_order,relevance_accuracy_list_union)

    print "-----relevance expert1-----"
    print_results(article_order,relevance_accuracy_list_expert1)

    print "-----relevance expert2-----"
    print_results(article_order,relevance_accuracy_list_expert2)

    print "------------------------------------"
    print "------------------------------------"
    print "-----irrelevance intersect-----"
    print_results(article_order,irrelevance_accuracy_list_intersect)
    
    print "-----irrelevance union-----"
    print_results(article_order,irrelevance_accuracy_list_union)

    print "-----irrelevance expert1-----"
    print_results(article_order,irrelevance_accuracy_list_expert1)

    print "-----irrelevance expert2-----"
    print_results(article_order,irrelevance_accuracy_list_expert2)

    #print "------------------------------------"
    #print irrelevance_annotations["expert1"]
    #print irrelevance_annotations["expert2"]
    #print irrelevance_annotations["expert-intersect"]
    #print irrelevance_annotations["expert-union"]

    #print "----------------------------"
    #cal_hit_count(workflow_id_list)
    
    """
    print "--------- topic annotation -------------------"
    print_annotation("topic","expert1",topic_annotations["expert1"])
    print_annotation("topic","expert2",topic_annotations["expert2"])
    print_annotation("topic","expert-intersect",topic_annotations["expert-intersect"])
    print_annotation("topic","expert-union",topic_annotations["expert-union"])
    print_annotation("topic","crowd1",topic_annotations["crowd1"])
    print_annotation("topic","crowd2",topic_annotations["crowd2"])

    print "---------- relevance annotation ------------------"
    print_annotation("relevance","expert1",relevance_annotations["expert1"])
    print_annotation("relevance","expert2",relevance_annotations["expert2"])
    print_annotation("relevance","expert-intersect",relevance_annotations["expert-intersect"])
    print_annotation("relevance","expert-union",relevance_annotations["expert-union"])
    print_annotation("relevance","crowd1",relevance_annotations["crowd1"])
    print_annotation("relevance","crowd2",relevance_annotations["crowd2"])

    print "---------- irrelevance annotation ------------------"
    print_annotation("irrelevance","expert1",irrelevance_annotations["expert1"])
    print_annotation("irrelevance","expert2",irrelevance_annotations["expert2"])
    print_annotation("irrelevance","expert-intersect",irrelevance_annotations["expert-intersect"])
    print_annotation("irrelevance","expert-union",irrelevance_annotations["expert-union"])
    print_annotation("irrelevance","crowd1",irrelevance_annotations["crowd1"])
    print_annotation("irrelevance","crowd2",irrelevance_annotations["crowd2"])
    """
    total_topics_size=0
    total_relevant_keywords_size=0
    for article_id in article_id_list:
        topics = [i[0] for i in topic_map[article_id]]
        total_topics_size = total_topics_size + sum(topics)
        r_keywords = [i[0] for i in relevant_keywords_map[article_id]]
        total_relevant_keywords_size = total_relevant_keywords_size + sum(r_keywords)


    print "topic annotations: %d" % total_topics_size
    print "relevance annotations: %d" % total_relevant_keywords_size