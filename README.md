# 546_AWS_Image_Recognition_Service 
Our cloud app will provide a face recognition service to users, by using cloud resources to perform deep learning on images provided by the users. The deep learning model will be provided as a service. This application will put a layer for the model to work.

Install Dependecies -

!/bin/bash

Download get-pip to current directory. It won't install anything, as of now

curl -O https://bootstrap.pypa.io/get-pip.py

Use python3.6 to install pip

python3 get-pip.py

This will install pip3 and pip3.6

pip3 install -r requirements.txt

### Web Tier IP and SSH Details

ssh -i "Akash_key.pem" ec2-user@ec2-3-86-234-121.compute-1.amazonaws.com

### Resources Used in AWS as Naming:

AWS_S3_INPUT_BUCKET_NAME = "cc-546-grp-11-input-bucket"

AWS_S3_OUTPUT_BUCKET_NAME = "cc-546-grp-11-output-bucket"

AWS_SQS_REQUEST_QUEUE_NAME = "images-requests"

AWS_SQS_RESPONSE_QUEUE_NAME = "images-responses"

REGION_NAME = "us-east-1"

AWS_ACCESS_KEY_ID = "AAAAAAAAAAAAAAA"

AWS_ACCESS_KEY_SECRET = "BBBBBBBBBBBBBBBB"

### We have also loaded the script at startup of the instance on AMI load:

!/bin/bash

sudo yum update -y

sudo yum install git -y

echo export AWS_ACCESS_KEY_ID="AAAAAAAAAAAAAAA" >> /etc/profile

echo export AWS_SECRET_ACCESS_KEY="BBBBBBBBBBBBBBBB"" >> /etc/profile

git clone https://token@github.com/akashkthkr/546_AWS_Image_Recognition_Service.git


### Team Members Group 11:
Akash Kant (akant1)

Ayush Kalani (akalani2)

Nakul Vaidya (nvaidya7)

