import base64

import boto3
from botocore.exceptions import ClientError
import logging
import os
import constants
import EC2AutoScaling
import SQSManagement
import subprocess


# Constants
S3_INPUT_BUCKET = constants.AWS_S3_INPUT_BUCKET_NAME
S3_OUTPUT_BUCKET = constants.AWS_S3_OUTPUT_BUCKET_NAME

SQS_REQUEST_QUEUE_NAME = constants.AWS_SQS_REQUEST_QUEUE_NAME
SQS_RESPONSE_QUEUE_NAME = constants.AWS_SQS_RESPONSE_QUEUE_NAME

# initialization and instantiations

sqs_management_instance = SQSManagement()
ec2_auto_scale_instance = EC2AutoScaling()

app_sqs_resource = boto3.resource("sqs", region_name=constants.REGION_NAME)
app_sqs_client = boto3.client('sqs', region_name=constants.REGION_NAME)

response_queue_url = sqs_management_instance.get_queue_url(SQS_RESPONSE_QUEUE_NAME)
request_queue_url = sqs_management_instance.get_queue_url(SQS_REQUEST_QUEUE_NAME)


def get_message(queue_url):
    try:
        sqs_response = app_sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            MessageAttributeNames=['All'],
            VisibilityTimeout=8,
            WaitTimeSeconds=20
        )
        message = sqs_response.get('Messages', None)
        return message[0] if message else None
    except ClientError as e:
        logging.error(e)


def send_message_to_queue_response(queue_url, image_name):
    try:
        response = app_sqs_client.send_message(QueueUrl=queue_url,
                                               MessageBody=image_name)
        print("send_message_to_queue_response :" + send_message_to_queue_response)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def delete_message_request(queue_url, receipt_handle):
    try:
        app_sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle
                                      )
    except ClientError as e:
        logging.error(e)
        return False
    return True


def store_image_to_s3(file_name, bucket_name, image_file):
    try:
        s3_client = boto3.client('s3')
        response = s3_client.upload_file(file_name, bucket_name, image_file)
        print("image_loaded")
    except ClientError as e:
        logging.error(e)


def write_to_file(image_name, result):
    with open(image_name, "wb") as f:
        f.write(bytes(result, 'utf8'))
        f.close()


def save_result_file_into_bucket(file_name, bucket_name, object_name):
    try:
        s3_client = boto3.client('s3')
        response = s3_client.upload_file(file_name, bucket_name, object_name)
    except ClientError as e:
        logging.error(e)


def shutting_down_instances():
    instance_ids = ec2_auto_scale_instance.get_instances_by_state()
    ec2_auto_scale_instance.stop_instances(instance_ids)
    return None


def get_image_after_decoding_base64(msg_value):
    return base64.decodestring(msg_value)

# this one is to be checked and completed
def get_output_from_classification(image_file_jpg):
    # os.chdir(r"../")
    classification_predicted_result = subprocess.check_output(["python3", "../face_recognition.py", image_file_jpg])
    print("classification_predicted_result :" + str(classification_predicted_result))
    return classification_predicted_result


def running_app_tier():
    while True:
        if sqs_management_instance.numberOfMessagesInQueue(SQS_RESPONSE_QUEUE_NAME):
            break
        message = get_message(sqs_management_instance.get_queue_url(SQS_REQUEST_QUEUE_NAME))
        if message is None:
            break
        msg_filename_key = message.get('key')
        print("msg_filename_key :" + msg_filename_key)
        msg_base64_encoded_value = message.get('value')
        print("msg_base64_encoded_value :" + msg_base64_encoded_value)
        transient_binary_file = msg_filename_key
        image_file_jpg = get_image_after_decoding_base64(msg_base64_encoded_value)
        print("image_file_jpg :" + image_file_jpg)
        store_image_to_s3(msg_filename_key, S3_INPUT_BUCKET, image_file_jpg)
        classified_predicted_result = get_output_from_classification(image_file_jpg)
        key_value_pair_predicted = '({0}, {1})'.format(msg_filename_key, classified_predicted_result)
        print("key_value_pair_predicted :" + key_value_pair_predicted)
        write_to_file(transient_binary_file, key_value_pair_predicted)
        print("S3_OUTPUT_BUCKET :" + S3_OUTPUT_BUCKET + " transient_binary_file :" +transient_binary_file )
        save_result_file_into_bucket(transient_binary_file, S3_OUTPUT_BUCKET, transient_binary_file)
        os.remove(transient_binary_file)
        send_message_to_queue_response(sqs_management_instance.get_queue_url(SQS_REQUEST_QUEUE_NAME), msg_filename_key)
        # deleting message after the message response is sent to queue
        delete_message_request(sqs_management_instance.get_queue_url(SQS_REQUEST_QUEUE_NAME), message['ReceiptHandle'])
    return None

if __name__ == '__main__':
    running_app_tier()
    shutting_down_instances()
