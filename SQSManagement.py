from asyncio import constants
import boto3
import logging
import constants
import os
from botocore.exceptions import ClientError

REQUEST_QUEUE_NAME = constants.AWS_SQS_REQUEST_QUEUE_NAME
RESPONSE_QUEUE_NAME = constants.AWS_SQS_RESPONSE_QUEUE_NAME

key = os.environ['AWS_ACCESS_KEY_ID']
secret = os.environ['AWS_SECRET_ACCESS_KEY']
print("key "+ key)
print("secret " +secret)

client = boto3.client('sqs', aws_access_key_id=key, aws_secret_access_key=secret,region_name=constants.REGION_NAME)

def create_SQS_queue(SQS_QUEUE_NAME=REQUEST_QUEUE_NAME):
    try:
        queue = client.create_queue(
            QueueName=SQS_QUEUE_NAME,
            Attributes={
                'DelaySeconds': '15',
                'MaximumMessageSize': '262144',
                'VisibilityTimeout': '60',
                'MessageRetentionPeriod': '86400'
            }
        )
        return queue['QueueUrl']
    except:
        logging.error(
            "Unable to create a SQS queue with the given name, recheck the queue name")


def get_queue_url(queue_name=REQUEST_QUEUE_NAME):
    return client.get_queue_url(QueueName=queue_name)['QueueUrl']

def send_message(queueUrl, msg):
    response = client.send_message(
        QueueUrl = queueUrl,
        MessageBody = msg,
        DelaySeconds = 123,
    )
    logging.debug(response.get('MessageId'))


def numberOfMessagesInQueue(queue_name=REQUEST_QUEUE_NAME):
    response = client.get_queue_attributes(
        QueueUrl=get_queue_url(queue_name),
        AttributeNames=[
            'All' | 'Policy' | 'VisibilityTimeout' | 'MaximumMessageSize' | 'MessageRetentionPeriod' | 'ApproximateNumberOfMessages' | 'ApproximateNumberOfMessagesNotVisible' | 'CreatedTimestamp',
        ]
    )
    logging.debug("numberOfMessagesInQueue %s %s", queue_name, int(response.ApproximateNumberOfMessages))
    return int(response.ApproximateNumberOfMessages)
