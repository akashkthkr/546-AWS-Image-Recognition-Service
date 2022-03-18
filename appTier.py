import base64

import boto3
from botocore.exceptions import ClientError
import logging
import os
import constants
import SQSManagement
from subprocess import check_output
import json

# Constants
S3_INPUT_BUCKET = constants.AWS_S3_INPUT_BUCKET_NAME
S3_OUTPUT_BUCKET = constants.AWS_S3_OUTPUT_BUCKET_NAME

SQS_REQUEST_QUEUE_NAME = constants.AWS_SQS_REQUEST_QUEUE_NAME
SQS_RESPONSE_QUEUE_NAME = constants.AWS_SQS_RESPONSE_QUEUE_NAME

# initialization and instantiations

sqs_management_instance = SQSManagement

# app_sqs_resource = boto3.resource("sqs", region_name=constants.REGION_NAME)
app_sqs_client = boto3.client('sqs',
                              region_name=constants.REGION_NAME, aws_access_key_id=constants.AWS_ACCESS_KEY_ID,
                                                                 aws_secret_access_key=constants.AWS_ACCESS_KEY_SECRET)

s3_client = boto3.client('s3', 
                         region_name=constants.REGION_NAME, aws_access_key_id=constants.AWS_ACCESS_KEY_ID,
                                                                 aws_secret_access_key=constants.AWS_ACCESS_KEY_SECRET)

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
        if message:
            return message[0]
        else:
            return None
    except ClientError as e:
        logging.error(e)



def send_message_to_queue_response(queue_url, image_classification_key_value):
    try:
        response = app_sqs_client.send_message(QueueUrl=queue_url,
                                               MessageBody=image_classification_key_value)
        print("send_message_to_queue_response")
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
        response = s3_client.upload_file(file_name, bucket_name, image_file)
        print("image_loaded")
    except ClientError as e:
        logging.error(e)


# def write_to_file(image_name, result):
#     with open(image_name, "rb") as f:
#         f.write(bytes(result, 'utf8'))
#         f.close()


def save_result_file_into_bucket(file_name, bucket_name, object_name):
    try:
        response = s3_client.upload_file(file_name, bucket_name, object_name)
    except ClientError as e:
        logging.error(e)


def get_image_after_decoding_base64(msg_filename_key, msg_value):
    msg_value = bytes(msg_value, 'utf-8')
    with open('encode.bin', "wb") as file:
        file.write(msg_value)
    file = open('encode.bin', 'rb')
    byte = file.read()
    file.close()
    decodeit = open(msg_filename_key, 'wb')
    decodeit.write(base64.b64decode((byte)))
    decodeit.close()
    os.remove("encode.bin")

def classify_image_sub(base64ImageStr, imageName):
    base64Image = bytes(base64ImageStr, 'utf-8')
    with open(imageName, "wb") as fh:
        fh.write(base64.decodebytes(base64Image))
    out = check_output(["python3", "-W ignore", "../face_recognition.py", imageName]).strip().decode('utf-8')
    return out


if __name__ == '__main__':
    while True:
        print("running_app_tier start")
        message = get_message(sqs_management_instance.get_queue_url())
        if message is None:
            continue
        payload = json.loads(message.get("Body"))
        msg_filename_key = payload.get('key')
        msg_base64_encoded_value = payload.get('value')
        # Getting the encoded message
        # Getting the Classified output
        classified_predicted_result = classify_image_sub(msg_base64_encoded_value, msg_filename_key)
        key_value_pair_predicted_json = json.dumps({'key': str(msg_filename_key), 'value': str(classified_predicted_result)})
        print("key_value_pair_predicted ")
        print(key_value_pair_predicted_json)
        print("Storing Image to S3")
        store_image_to_s3(msg_filename_key, S3_INPUT_BUCKET, msg_filename_key)
        print("S3_OUTPUT_BUCKET :" + S3_OUTPUT_BUCKET + " Image File Name :" + msg_filename_key)
        save_result_file_into_bucket(msg_filename_key, S3_OUTPUT_BUCKET, msg_filename_key)
        print("Saved to s3 output bucket")
        # removing the Image png File
        send_message_to_queue_response(sqs_management_instance.get_queue_url(SQS_RESPONSE_QUEUE_NAME), key_value_pair_predicted_json)
        # os.remove(msg_filename_key)
        # Deleting message after the message response is sent to queue
        delete_message_request(sqs_management_instance.get_queue_url(), message['ReceiptHandle'])
