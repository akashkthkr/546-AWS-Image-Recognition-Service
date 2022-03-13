import boto3

client = boto3.client('sqs')
QUEUE_NAME="images-requests-1"

def create_SQS_queue(SQS_QUEUE_NAME=QUEUE_NAME):
    try:
        queue = client.create_queue( 
            QueueName = SQS_QUEUE_NAME, 
            Attributes = { 
                'DelaySeconds':'15',
                'MaximumMessageSize':'262144',
                'VisibilityTimeout':'3600',
                'MessageRetentionPeriod':'86400'
            }     
        )
        print(queue.url)
        return queue
        raise
    except:
        print("Unable to create a SQS queue with the given name, recheck the queue name")

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
  print(response.get('MessageId'))
        
create_SQS_queue()