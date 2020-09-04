#!/usr/bin/python

"""Site Deployer: Deploy websites with aws.
Webotron automates the process of deploying static websites to AWS.
- Configure AWS S3 buckets
  - Create them
  - Set them up for static website hosting
  - Deploy local files to them
- Configure DNS with AWS Route 53
- Configure a Content Delivery Network and SSL with AWS CloudFront
"""
import sys
import os
import subprocess
import string
import random
import boto3
from botocore.exceptions import ClientError
from bucket import BucketManager

profile_name = 'default'
# session = None 
# bucket_manager = None

# Checking if any argument was provided.
# When You need to change your aws for this script use "-p <profile_name>"
# To change your default profile
if len(sys.argv) >= 2:
    if(sys.argv[1] == "-p"):
      profile_name = sys.argv[2]
      print('profile switched to',profile_name)
else:
    print("No profile provided. Using 'default' ")  
  
 
# defining s3 object
s3 = None

# Generating a random bucket name string
def generate_string():
    letters = string.ascii_lowercase
    join_letters = ''.join(random.choice(letters) for i in range(15))
    return 'aws-python-' + join_letters
    
bucket_name = generate_string() 
print("will create bucket with name: \n",bucket_name)


# Connecting to AWS account named "default" using boto3 library

try:
    session = boto3.Session(profile_name=profile_name)
except :
    profile_list = os.system('cat ~/.aws/config')
    profile_list = subprocess.run(["cat ~/.aws/config"], stdout=subprocess.PIPE, text=True, input="All available profiles are bellow: \n")
    print(profile_list.stdout) 
    print("Session creation failed for the following profile : \n",profile_name)
    print("Please use current profile name from the available bellow: \n",profile_list.stdout)
    
bucket_manager = BucketManager(session)

# 
def setup_bucket(bucket_name):
    s3_bucket = bucket_manager.init_bucket(bucket_name)
    bucket_manager.set_policy(bucket_name,s3_bucket)
    bucket_manager.configure_website(s3_bucket)
    # Print out the website URL:
    url = f'http://{bucket_name}.s3-website-us-east-1.amazonaws.com/'
    print(url)
    return

# 
def sync(pathname, bucket_name):
    """Sync contents in directory: PATHNAME to our S3 BUCKET."""
    bucket_manager.sync(pathname, bucket_name)

# 
setup_bucket(bucket_name)
sync('sample_site', bucket_name)

# List all buckets
for bucket in bucket_manager.all_buckets():
    print(bucket)


# List all Objects in a newly created Bucket:
for object in bucket_manager.all_objects(bucket_name):
    print('New bucket contains following ojects: \n',object)