REGION_NAME = "us-east-1"
SECURITY_GROUP_ID = ["sg-0bb98ead470e1d287"]
#APP_TIER_AMI = "ami-0a55e620aa5c79a24" OG IMAGE
APP_TIER_AMI="ami-0a3cffc7ceda79086"
INSTANCE_TYPE = 't2.micro'
AWS_S3_INPUT_BUCKET_NAME = "cc-546-grp-11-input-bucket"
AWS_S3_OUTPUT_BUCKET_NAME = "cc-546-grp-11-output-bucket"
AWS_SQS_REQUEST_QUEUE_NAME = "images-requests"
AWS_SQS_RESPONSE_QUEUE_NAME = "images-responses"
AWS_ACCESS_KEY_ID = ""
AWS_ACCESS_KEY_SECRET = ""
## SWAG
STARTUP_BANNER =f"""
 +-+ +-+ +-+ +-+ +-+   +-+ +-+ +-+ +-+ +-+ +-+ +-+ +-+ +-+
 |C| |l| |o| |u| |d|   |C| |o| |m| |p| |u| |t| |i| |n| |g|
 +-+ +-+ +-+ +-+ +-+   +-+ +-+ +-+ +-+ +-+ +-+ +-+ +-+ +-+
"""

STARTUP_BANNER_GROUP = f"""
  _______ .______        ______    __    __  .______       __   __  
 /  _____||   _  \      /  __  \  |  |  |  | |   _  \     /_ | /_ | 
|  |  __  |  |_)  |    |  |  |  | |  |  |  | |  |_)  |     | |  | | 
|  | |_ | |      /     |  |  |  | |  |  |  | |   ___/      | |  | | 
|  |__| | |  |\  \----.|  `--'  | |  `--'  | |  |          | |  | | 
 \______| | _| `._____| \______/   \______/  | _|          |_|  |_| 
"""