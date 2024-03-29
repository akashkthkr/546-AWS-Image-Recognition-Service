import boto3
import logging
import SQSManagement
import time, os, sys
import constants
from botocore.exceptions import ClientError
from random import randrange

logging.basicConfig(filename='ec2AutoScaling.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
MAX_LIMIT_INSTANCES = 19
EC2_KEY_NAME = "ec2-key-pair"
USER_DATA = f"""#!bin/bash
cd /home/ec2-user/546_AWS_Image_Recognition_Service
git pull
python3 appTier.py
"""

ec2_client = boto3.client('ec2', region_name=constants.REGION_NAME, aws_access_key_id=constants.AWS_ACCESS_KEY_ID,
                                                                 aws_secret_access_key=constants.AWS_ACCESS_KEY_SECRET)
ec2_res = boto3.resource('ec2', region_name=constants.REGION_NAME, aws_access_key_id=constants.AWS_ACCESS_KEY_ID,
                                                                 aws_secret_access_key=constants.AWS_ACCESS_KEY_SECRET)

def create_key_pair():
    try:
        key_pair = ec2_client.create_key_pair(KeyName=EC2_KEY_NAME)
        private_key = key_pair["KeyMaterial"]
        # write private key to file with 400 permissions
        with os.fdopen(os.open("/tmp/aws_ec2_key.pem", os.O_WRONLY | os.O_CREAT, 0o400), "w+") as handle:
            handle.write(private_key)
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print("Key pair already exists")
        else:
            print("Unexpected error: %s" % e)

def create_security_group():
    response = ec2_client.create_security_group(
        Description='string',
        GroupName='string',
        VpcId='string',
        TagSpecifications=[
            {'ResourceType': 'export-image-task',
             'Tags': [
                 {
                     'Key': 'cloud-test-1',
                     'Value': 'cloud-test-1'
                 },
             ]
             },
        ],
        DryRun=False
    )

def create_instance(min_count=1, max_count=1):
    try:
        logging.debug("Creating %s new instance(s)", max_count)
        instances = ec2_res.create_instances(
            ImageId=constants.APP_TIER_AMI,
            MinCount=min_count,
            MaxCount=max_count,
            InstanceType=constants.INSTANCE_TYPE,
            SecurityGroupIds=constants.SECURITY_GROUP_ID,
            UserData=USER_DATA
        )
        current_running_count = len(get_instances_by_state())
        for instance in instances:
            current_running_count+=1
            ec2_res.create_tags(Resources=[instance.id], Tags=[
                {
                    'Key': 'Name',
                    'Value': "app-instance-" + str(current_running_count),
                },
            ])
    except ClientError as e:
        print("Unexpected error: %s" % e)

def stop_instances(instance_ids):
    if len(instance_ids) == 0:
          return
    logging.debug("Stopping instance: %s", instance_ids)
    response = ec2_client.stop_instances(InstanceIds=instance_ids)
    logging.debug(response)


def terminate_instance(instance_ids):
    if len(instance_ids) == 0:
          return
    logging.debug("Stopping instance: %s", instance_ids)
    response = ec2_client.terminate_instances(InstanceIds=instance_ids)
    logging.debug(response)


def get_instances_by_state(state=['running']):
    filters = [
        {
            'Name': 'instance-state-name',
            'Values': state
        },
        {
            'Name': 'image-id',
            'Values': [constants.APP_TIER_AMI]
        }
    ]
    instances = ec2_res.instances.filter(Filters=filters)
    for instance in instances:
        print("running instance - " + instance.id)
        logging.debug(instance.id)
    return [instance.id for instance in instances]


def auto_scale_instances():
    queue_length = SQSManagement.numberOfMessagesInQueue()
    logging.debug("Request queue length: %s", queue_length)
    print("Request queue length:", queue_length)

    if queue_length == 0:
        logging.debug("No Request in queue ****SCALE IN****, stopping all instances")
        # make sure the instance is idle and do not stop if it is currenlty processing a request
        terminate_instance(get_instances_by_state())
    else:
        number_of_running_instances = len(get_instances_by_state())
        number_of_pending_instances = len(get_instances_by_state(['pending']))
        # if some instances are starting up, cool down
        if number_of_pending_instances > 0:
            return
        logging.debug("Number of running instances: %s", number_of_running_instances)
        if number_of_running_instances >= MAX_LIMIT_INSTANCES or number_of_pending_instances >= MAX_LIMIT_INSTANCES:
            logging.debug("Infra at MAX CAPACITY %s, can not scale out", MAX_LIMIT_INSTANCES)
            return
        # scale up
        if number_of_running_instances < queue_length:
            total_instances_to_spawn = min(queue_length - number_of_running_instances, MAX_LIMIT_INSTANCES)
            logging.debug("Number of total_instances_to_spawn %s", total_instances_to_spawn)
            stopped_instances_id_list = get_instances_by_state(['stopped'])
            num_of_stopped_instances = len(stopped_instances_id_list)
            logging.debug("Number of stopped_instances %s", num_of_stopped_instances)

            new_instances_required = 0
            if total_instances_to_spawn - num_of_stopped_instances > 0:
                new_instances_required = total_instances_to_spawn - num_of_stopped_instances
            # Start the stopped instances, if any
            if num_of_stopped_instances > 0:
                ec2_client.start_instances(InstanceIds=stopped_instances_id_list)
            # Start remainder new instances
            if new_instances_required > 0:
                logging.debug(" Starting %s new instances", new_instances_required)
                create_instance(min_count=new_instances_required, max_count=new_instances_required)
        # scale down
        if number_of_running_instances > queue_length:
            # stop half of the instances
            return

while True:
    logging.info(constants.STARTUP_BANNER)
    logging.info(constants.STARTUP_BANNER_GROUP)
    logging.debug("*********** Started EC2 auto scaling according to queue length**************")
    auto_scale_instances()
    time.sleep(10)