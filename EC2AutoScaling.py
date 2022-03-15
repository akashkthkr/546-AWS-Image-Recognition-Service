import boto3
import logging
import SQSManagement
import time, os, sys
import constants
from botocore.exceptions import ClientError

logging.basicConfig(filename='ec2AutoScaling.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)

AMI = "ami-0a55e620aa5c79a24"
MAX_LIMIT_INSTANCES = 3
EC2_KEY_NAME = "ec2-key-pair"
USER_DATA = f"""#!bin/bash
yum update -y
yum install git -y
"""
ec2_client = boto3.client('ec2', region_name=constants.REGION_NAME)
ec2_res = boto3.resource('ec2', region_name=constants.REGION_NAME)

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
        { 'ResourceType': 'export-image-task',
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
    logging.debug("Creating new instance")
    instances = ec2_res.create_instances(
        ImageId=constants.APP_TIER_AMI,
        MinCount=min_count,
        MaxCount=max_count,
        InstanceType=constants.INSTANCE_TYPE,
        SecurityGroupIds=constants.SECURITY_GROUP_ID,
        UserData=USER_DATA
    )
    for instance in instances:
      ec2_res.create_tags(Resources=[instance[0].id], Tags=[
          {
              'Key': 'Name',
              'Value': "app-instance1",
          },
      ])
  except ClientError as e:
    print("Unexpected error: %s" % e)

def stop_instances(instance_ids):
    logging.debug("Stopping instance:", instance_ids)
    response = ec2_client.stop_instances(InstanceIds=instance_ids)
    logging.debug(response)

def terminate_instance(instance_ids):
    logging.debug("Terminating instance:", instance_ids)
    response = ec2_client.terminate_instances(InstanceIds=instance_ids)
    logging.debug(response)
    
def get_instances_by_state(state = ['running']):
    filters = [
        {
          'Name': 'instance-state-name', 
          'Values': state
        }, 
        {
          'Name': 'ImageId',
           'Values': state
        }
    ]
    instances = ec2_res.instances.filter(Filters=filters)
    for instance in instances:
      logging.debug(instance.id)
    return [instance.id for instance in instances]

def auto_scale_instances():
    queue_length = 3#SQSManagement.numberOfMessagesInQueue()
    logging.debug("Request queue length:", queue_length)

    if queue_length == 0:
        logging.debug("No Request in queue ****SCALE IN****, stopping all instances")
        # make sure the instance is idle and do not stop if it is currenlty processing a request
        stop_instances(get_instances_by_state())
    else: 
        number_of_running_instances = len(get_instances_by_state())
        logging.debug("Number of running instances:", number_of_running_instances)
        if number_of_running_instances >= MAX_LIMIT_INSTANCES:
            logging.debug("Infra at MAX CAPACITY %s, can not scale out", MAX_LIMIT_INSTANCES)
            return
        # scale up
        if number_of_running_instances < queue_length:
            more_instances_required = min(queue_length - number_of_running_instances, MAX_LIMIT_INSTANCES)
            stopped_instances_id_list = get_instances_by_state(['stopped'])
            num_of_stopped_instances = len(stopped_instances_id_list)
            
            new_instances_required = 0
            if more_instances_required - num_of_stopped_instances > 0:
              new_instances_required = more_instances_required - num_of_stopped_instances
             
            # Start the stopped instances
            ec2_client.start_instances(InstanceIds=stopped_instances_id_list)
            # Start remainder new instances
            if new_instances_required>0:
              create_instance(min_count=new_instances_required, max_count=new_instances_required)
            
# while True:
#     logging.debug("starting auto scaling")
#     auto_scale_instances()
#     time.sleep(30)