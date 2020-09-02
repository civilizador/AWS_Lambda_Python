import boto3
import string
import random
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

# Upload an object to new bucket:
s3.Bucket(bucket_name).upload_file('index.html', 'index.html',ExtraArgs={'ContentType':'text/html'})
s3.Bucket(bucket_name).upload_file('index.html', '404.html',ExtraArgs={'ContentType':'text/html'})
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