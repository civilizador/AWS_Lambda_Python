import boto3
import string
import random

def generate_string():
    letters = string.ascii_lowercase
    join_letters = ''.join(random.choice(letters) for i in range(15))
    return 'aws-python-' + join_letters

bucket_name = generate_string() 
print("will create bucket with name: \n",bucket_name)

# Connecting to AWS account named "default" using boto3 library
session = boto3.Session(profile_name='default')

# Connecting to resource : "s3"
s3 = session.resource('s3')

# Creating new s3 bucket with random name:
s3.create_bucket(
    Bucket = bucket_name,
)

# Upload an object to new bucket:
s3.Bucket(bucket_name).upload_file('Configuring_env.txt', 'config.txt')

# List all buckets
for bucket in s3.buckets.all():
    print(bucket)

# List all Objects in a newly created Bucket:
for object in s3.Bucket(bucket_name).objects.all():
    print('New bucket contains following ojects: \n',object)
