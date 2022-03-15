import boto3
import logging

REQUEST_QUEUE_NAME = "images-requests"
RESPONSE_QUEUE_NAME = "images-response"

client = boto3.client('sqs')

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


def get_queue_url(queue_name):
    return client.get_queue_url(QueueName=queue_name)['QueueUrl']

def send_message():
    response = client.send_message(
        QueueUrl='string',
        MessageBody='string',
        DelaySeconds=123,
        MessageAttributes={
            'string': {
                'StringValue': 'string',
                'BinaryValue': b'bytes',
                'StringListValues': [
                    'string',
                ],
                'BinaryListValues': [
                    b'bytes',
                ],
                'DataType': 'string'
            }
        },
        MessageSystemAttributes={
            'string': {
                'StringValue': 'string',
                'BinaryValue': b'bytes',
                'StringListValues': [
                    'string',
                ],
                'BinaryListValues': [
                    b'bytes',
                ],
                'DataType': 'string'
            }
        },
        MessageDeduplicationId='string',
        MessageGroupId='string'
    )
    logging.debug(response.get('MessageId'))


def numberOfMessagesInSQS(queue_name):
    response = client.get_queue_attributes(
        QueueUrl=get_queue_url(queue_name),
        AttributeNames=[
            'All' | 'Policy' | 'VisibilityTimeout' | 'MaximumMessageSize' | 'MessageRetentionPeriod' | 'ApproximateNumberOfMessages' | 'ApproximateNumberOfMessagesNotVisible' | 'CreatedTimestamp',
        ]
    )
    logging.debug("numberOfMessagesInSQS %s %s", queue_name, int(response.ApproximateNumberOfMessages))
    return int(response.ApproximateNumberOfMessages)