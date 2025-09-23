from atlassian.bitbucket import Cloud
import os

# Assuming these environment variables are set and correct
BITBUCKET_EMAIL = os.environ.get("BITBUCKET_EMAIL")
BITBUCKET_APP_PASSWORD = os.environ.get("BITBUCKET_APP_PASSWORD")
BITBUCKET_WORKSPACE = os.environ.get("BITBUCKET_WORKSPACE")

try:
    client = Cloud(
        url='https://api.bitbucket.org/',
        username='insertUserNameHere',         # Use the env var
        password='insertAPIAuthTokenHere'   # Use the env var
    )
    print(f"Client type: {type(client)}")
    print(f"Does client have 'repositories' attribute? {hasattr(client, 'repositories')}")

    if hasattr(client, 'repositories'):
        repo_module = client.repositories
        print(f"Type of repositories module: {type(repo_module)}")
        print(f"Does repositories module have 'get_all_repositories' attribute? {hasattr(repo_module, 'get_all_repositories')}")
        print(f"Does repositories module have 'iterator' attribute? {hasattr(repo_module, 'iterator')}")

        # Try to fetch one repository if you know a valid slug in your workspace
        # For example:
        # try:
        #     single_repo = repo_module.get(BITBUCKET_WORKSPACE, "your-repo-slug-here")
        #     print(f"Successfully fetched a single repo: {single_repo['name']}")
        # except Exception as e:
        #     print(f"Error fetching single repo: {e}")

        # If the above methods are still missing, this is the lowest level you can go
        # to list repositories using the client's direct HTTP methods.
        try:
            print("Attempting low-level API call to list repositories...")
            response = client.get(f"repositories/{BITBUCKET_WORKSPACE}")
            print("Low-level API call successful. First 5 repos (if any):")
            if isinstance(response, dict) and 'values' in response:
                for i, repo in enumerate(response['values'][:5]):
                    print(f"  - {repo['slug']}")
            else:
                print(f"  Unexpected response format: {response}")
        except Exception as e:
            print(f"Error with low-level API call: {e}")

    else:
        print("Client does NOT have 'repositories' attribute. This is unexpected.")

except Exception as e:
    print(f"Initialization or basic test failed: {e}")