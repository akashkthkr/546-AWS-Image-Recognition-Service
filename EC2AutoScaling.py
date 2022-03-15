import boto3
import logging
import SQSManagement

ec2_client = boto3.client('ec2', region_name="us-east-1")
ec2_res = boto3.resource('ec2')

USER_DATA = f"""#!bin/bash
yum update -y
"""
AMI = "ami-0a55e620aa5c79a24"
MAX_LIMIT_INSTANCES = 19

def create_instance(key_name, sec_group_ids, instance_type='t2.micro', min_count=1, max_count=1):
    logging.debug("Creating new instance")
    instance = ec2_res.create_instances(
        ImageId=AMI,
        MinCount=min_count,
        MaxCount=max_count,
        InstanceType=instance_type,
        KeyName=key_name,
        SecurityGroupIds=[sec_group_ids],
        UserData=USER_DATA
    )
    logging.debug("Instance created id:", instance["Instances"][0]["InstanceId"])

# if we stop, we can use this to avoid instance cold start times
# instance = conn.get_all_instances(instance_ids=['instance_id'])
# print instance[0].instances[0].start()

def stop_instances(instance_ids):
    logging.debug("Stopping instance:", instance_ids)
    response = ec2_client.stop_instances(InstanceIds=instance_ids)
    logging.debug(response)

def terminate_instance(instance_id):
    logging.debug("Terminating instance:", instance_id)
    response = ec2_client.terminate_instances(InstanceIds=[instance_id])
    logging.debug(response)
    
def get_instances_by_state(state = ['running']):
    filters = [
        {
          'Name': 'instance-state-name', 
          'Values': state
        }
    ]
    instances = ec2_res.instances.filter(Filters=filters)
    return [instance.id for instance in instances]

def auto_scale_instances():
    queue_length = SQSManagement.numberOfMessagesInQueue()
    logging.debug("Request queue length:", queue_length)

    if queue_length == 0:
        logging.debug("No Request in queue ****SCALE IN****, stopping all instances")
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
            num_of_stopped_instances = len(get_instances_by_state(['stopped']))
            new_instances_required = 0
            if more_instances_required - num_of_stopped_instances > 0:
              new_instances_required = more_instances_required - num_of_stopped_instances
              
            # first start the stopped instances

while True:
    logging.debug("starting auto scaling")
    auto_scale_instances()
    time.sleep(30)