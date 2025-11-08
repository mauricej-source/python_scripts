import os
from atlassian import Bitbucket

# --- Bitbucket API Client ---
try:
    bitbucket = Bitbucket(
        url='https://api.bitbucket.org/',
        username='mjohnson',
        password='BJWill@74',
        cloud=True
    )
    print(f"Bitbucket client object type: {type(bitbucket)}") # Add this
    print(f"Is bitbucket object valid? {bool(bitbucket)}") # Add this
except Exception as e:
    print(f"Error initializing Bitbucket client: {e}")
    print("Please ensure mjohnson and BITBUCKET_APP_PASSWORD environment variables are set.")
    exit()