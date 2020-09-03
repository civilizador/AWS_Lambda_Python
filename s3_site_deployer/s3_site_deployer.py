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
from pathlib import Path 
import mimetypes 
import string
import random
import boto3
from botocore.exceptions import ClientError



def generate_string():
    letters = string.ascii_lowercase
    join_letters = ''.join(random.choice(letters) for i in range(15))
    return 'aws-python-' + join_letters


# defining s3 object
s3 = None

bucket_name = generate_string() 
print("will create bucket with name: \n",bucket_name)


# Connecting to AWS account named "default" using boto3 library
session = boto3.Session(profile_name='default')


# Connecting to resource : "s3"
s3 = session.resource('s3')


# Creating new s3 bucket with random name:
# If creation of new bucket failed throw an error.
try:
    s3.create_bucket(
        Bucket = bucket_name,
    )
except ClientError as err:
    print(err)

def upload_to_s3(s3_bucket, path, key):
    content_type = mimetypes.guess_type(key)[0] or 'text/plain'
    s3_bucket.upload_file(
        path,
        key,
        ExtraArgs={ 
            'ContentType': content_type 
        }
    )

def sync(pathname):
    "Sync content of provided PATHNAME to BUCKET."
    s3_bucket = s3.Bucket(bucket_name)

    # Creating Universal(Win and Unix) path to website files that we need to upload.
    root = Path(pathname).expanduser().resolve()

    def handle_directory(website_dir):
        for item in website_dir.iterdir():
            if item.is_dir(): handle_directory(item)
            # If file, upload it to s3 using full path
            if item.is_file(): upload_to_s3(s3_bucket, str(item), str(item.relative_to(root).as_posix() ) )
    handle_directory(root)
sync('sample_site')

# Upload an object to new bucket:
s3.Bucket(bucket_name).upload_file('sample_site/index.html', 'index.html',ExtraArgs={'ContentType':'text/html'})
s3.Bucket(bucket_name).upload_file('sample_site/404.html', '404.html',ExtraArgs={'ContentType':'text/html'})
# List all buckets
for bucket in s3.buckets.all():
    print(bucket)

# List all Objects in a newly created Bucket:
for object in s3.Bucket(bucket_name).objects.all():
    print('New bucket contains following ojects: \n',object)

# Describing S3 bucket POLICY and saving it in the string
policy = f""" 
{{
  "Version":"2012-10-17",
  "Statement":[
    {{
      "Sid":"PublicRead",
      "Effect":"Allow",
      "Principal": "*",
      "Action":["s3:GetObject","s3:GetObjectVersion"],
      "Resource":["arn:aws:s3:::{bucket_name}/*"]
    }}
  ]
}}
"""

# Creating a Policy object
policy_object = s3.Bucket(bucket_name).Policy()

# Passing our predefined policy string to the Policy object 
policy_object.put(Policy = policy.strip())
print(policy_object)

# Creating website configuration object
website_object = s3.Bucket(bucket_name).Website()

# Defining Web configuration as object
web_config = {
    'ErrorDocument': {
        'Key': '404.html'
    },
    'IndexDocument': {
        'Suffix': 'index.html'
    }
}
# Passing our predefined Website configuration string to the Web Site object 
website_object.put(WebsiteConfiguration=web_config)

# Print out the website URL:
url = f'http://{bucket_name}.s3-website-us-east-1.amazonaws.com/'
print(url)