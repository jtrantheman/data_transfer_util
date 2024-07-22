import argparse
import urllib3
import time
from util_s3 import read_config, create_s3_client

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser(description='Copy a specific object from one S3 bucket to another.')
parser.add_argument('src_bucket', type=str, help='The source S3 bucket name.')
parser.add_argument('dst_bucket', type=str, help='The destination S3 bucket name.')

parser.add_argument('src_key', type=str, help='The source object key to copy.')
parser.add_argument('dst_key', type=str, help='The destination object key for the copied object.')

parser.add_argument('src_endpoint_url', type=str, help='The source endpoint url for the copied object.')
parser.add_argument('dst_endpoint_url', type=str, help='The destination endpoint url for the copied object.')

args = parser.parse_args()

###
# BEGIN: LOAD IN CONFIGURATIONS
###
config = read_config()

if not config:
    print("Failed to read the configuration.")
    quit()

src_region = config["src"]["region"]
src_access_key = config['src']['access_key']
src_secret_access_key = config['src']['secret_access_key']

dst_region = config["dst"]["region"]
dst_access_key = config['dst']['access_key']
dst_secret_access_key = config['dst']['secret_access_key']
###
# END: LOAD IN CONFIGURATIONS
###

# create our source and destination s3 clients so we can interact with our buckets
src_s3_client = create_s3_client(src_access_key, src_secret_access_key, src_region, args.src_endpoint_url)
dst_s3_client = create_s3_client(dst_access_key, dst_secret_access_key, dst_region, args.dst_endpoint_url)

# Record the start time
start_time = time.time()

# Stream the object directly directly
if src_region == 'snow': 
    s3_object = src_s3_client.meta.client.get_object(Bucket=args.src_bucket, Key=args.src_key)
else:
    s3_object = src_s3_client.get_object(Bucket=args.src_bucket, Key=args.src_key)
# Upload the streamed object to the destination
if dst_region == 'snow':
    dst_s3_client.put_object(Bucket=args.dst_bucket, Key=args.dst_key, Body=s3_object['Body'].read())
else:
    dst_s3_client.upload_fileobj(s3_object['Body'], args.dst_bucket, args.dst_key)

# Record the end time
end_time = time.time()

# Calculate and print the elapsed time
elapsed_time = end_time - start_time
print(f"Object '{args.src_key}' has been copied to '{args.dst_key}' in {elapsed_time:.2f} seconds using {args.src_endpoint_url} to {args.dst_endpoint_url}.")