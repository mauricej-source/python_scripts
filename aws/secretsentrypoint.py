import boto3
import os
import subprocess
import sys
from botocore.exceptions import ClientError

def get_secrets():
    secret_name = os.getenv('AWS_SECRET_ID')
    region_name = os.getenv('AWS_REGION', 'us-east-1')

    if not secret_name:
        print("No AWS_SECRET_ID found, skipping Secrets Manager.")
        return {}

    # Initialize the AWS Client
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        # Secrets are typically stored as a JSON string
        return get_secret_value_response['SecretString']
    except ClientError as e:
        print(f"Error fetching secret: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Fetch secrets and print/log (be careful not to log actual secrets in prod!)
    secrets = get_secrets()
    
    # In a real scenario, you would export these to the environment 
    # or write them to a temp config file for the Rails/Python app to read.
    print("Secrets fetched successfully. Starting application...")
    
    # Execute the main application command (e.g., rails server)
    subprocess.run(sys.argv[1:])