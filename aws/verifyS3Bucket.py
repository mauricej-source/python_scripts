import boto3
import sys

def check_bucket_encryption(bucket_name):
    client = boto3.client('s3')
    try:
        response = client.get_bucket_encryption(Bucket=bucket_name)
        rules = response['ServerSideEncryptionConfiguration']['Rules']
        print(f"✅ Bucket {bucket_name} is encrypted.")
    except Exception as e:
        print(f"⚠️ Warning: Bucket {bucket_name} has no encryption or access error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # In a real pipeline, bucket name would come from an environment variable
    check_bucket_encryption('creyos-production-assets')