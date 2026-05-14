import os
import boto3
from botocore.client import Config

# 1. Configure the connection to local MinIO
s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:9000',
    aws_access_key_id='admin',
    aws_secret_access_key='password',
    config=Config(signature_version='s3v4'),
)

bucket_name = 'bronze'

# 2. Create the bucket if it doesn't exist
try:
    s3.head_bucket(Bucket=bucket_name)
    print(f"Bucket {bucket_name} exists.")
except:
    s3.create_bucket(Bucket=bucket_name)
    print(f"Created bucket {bucket_name}.")

# 3. Iterate through the data directory and upload CSV files
data_dir = 'data'
for filename in os.listdir(data_dir):
    if filename.endswith(".csv"):
        local_path = os.path.join(data_dir, filename)

        print(f"Uploading {filename}...")
        s3.upload_file(local_path, bucket_name, filename)

print("All files uploaded successfully!")