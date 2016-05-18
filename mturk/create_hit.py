import os
import boto.mturk.connection
import boto.mturk.question
from config import config
from crowdtask.enum import TaskType

SANDBOX = config.getboolean('HIT Configuration', 'using_sandbox')
ACCESS_ID = config.get('AWS Access', 'aws_access_key_id')
SECRET_KEY = config.get('AWS Access', 'aws_secret_access_key')
HOST_SERVER = config.get('Server', 'hostname')

if SANDBOX == True:
    HOST = 'mechanicalturk.sandbox.amazonaws.com'
else:
    HOST = 'mechanicalturk.amazonaws.com'

print SANDBOX
print ACCESS_ID
print SECRET_KEY
print HOST
print HOST_SERVER

mturk = boto.mturk.connection.MTurkConnection(aws_access_key_id=ACCESS_ID, aws_secret_access_key=SECRET_KEY, host=HOST)


taskType="topic"
articleId="1"

def create_topic_hit():
    URL = '%s/mturk?taskType=%s&article_id=%s&using_sandbox=%s' % (HOST_SERVER, taskType, articleId, str.lower(str(SANDBOX)))
    title = "Find topic sentences in the paragraph"
    description = "Please find the topic sentence in the article"
    keywords = ["annotation", "feedback", "topic sentence"]
    frame_height = 500 # the height of the iframe holding the external hit
    amount = .05

    
    print mturk.get_account_balance()

    questionform = boto.mturk.question.ExternalQuestion( URL, frame_height )

    create_hit_result = mturk.create_hit(
        title = title,
        description = description,
        keywords = keywords,
        question = questionform,
        reward = boto.mturk.price.Price( amount = amount),
        response_groups = ( 'Minimal', 'HITDetail' ), # I don't know what response groups are
    )


    HIT = create_hit_result[0]
    assert create_hit_result.status

    print '[create_hit( %s, $%s ): %s]' % ( URL, amount, HIT.HITId )

#general
def create_hit():
    return

if __name__ == "__main__":
    create_topic_hit()
    print "go"
