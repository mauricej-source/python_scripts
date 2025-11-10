import os
# from atlassian import Bitbucket # REMOVED
from atlassian.bitbucket import Cloud # CORRECT IMPORT
import base64
import re
import yaml # For parsing YAML for potential metadata

# --- Configuration ---
# You can remove BITBUCKET_USERNAME if not using it for anything else.
# Keeping BITBUCKET_EMAIL for clarity as that's what's used for login.
BITBUCKET_EMAIL = os.environ.get("BITBUCKET_EMAIL")
BITBUCKET_APP_PASSWORD = os.environ.get("BITBUCKET_APP_PASSWORD")
BITBUCKET_WORKSPACE = os.environ.get("BITBUCKET_WORKSPACE")

# Keywords to identify Terraform files and potential modules/boilers
TERRAFORM_FILE_EXTENSIONS = ('.tf', '.tfvars')
TERRAFORM_MODULE_INDICATORS = [
    'module "',
    'source = "./',
    'source = "git::',
    'source = "bitbucket.org/'
]
BOILERPLATE_KEYWORDS = [
    'boilerplate',
    'template',
    'standard',
    'foundation',
    'common',
    'shared-module',
    'golden-path'
]

# --- Bitbucket API Client ---
bitbucket = None
try:
    # --- CRITICAL FIX 1: Use environment variables for credentials ---
    # --- CRITICAL FIX 2: REMOVE 'cloud=True' from Cloud constructor ---
    bitbucket = Cloud(
        url='https://api.bitbucket.org/',
        username=BITBUCKET_EMAIL,
        password=BITBUCKET_APP_PASSWORD
        # cloud=True # <--- REMOVED THIS LINE
    )
    print(f"DEBUG: Bitbucket client object created. Type: {type(bitbucket)}")
    print(f"DEBUG: Is bitbucket object valid? {bool(bitbucket)}")
    
    # Optional: Add checks for env var loading if you haven't already
    print(f"DEBUG: BITBUCKET_EMAIL loaded: {BITBUCKET_EMAIL if BITBUCKET_EMAIL else 'None'}")
    print(f"DEBUG: BITBUCKET_APP_PASSWORD loaded: {'*' * len(BITBUCKET_APP_PASSWORD) if BITBUCKET_APP_PASSWORD else 'None'}")
    print(f"DEBUG: BITBUCKET_WORKSPACE loaded: {BITBUCKET_WORKSPACE if BITBUCKET_WORKSPACE else 'None'}")

    # --- REMOVE THIS ENTIRE DEBUG BLOCK - IT'S NO LONGER RELEVANT FOR Cloud CLASS ---
    # if hasattr(bitbucket, 'cloud') and isinstance(bitbucket.cloud, bool):
    #     print(f"DEBUG: WARNING: bitbucket.cloud is a boolean ({bitbucket.cloud}) not an object. "
    #           f"Using direct top-level methods for API calls.")
    # else:
    #     print(f"DEBUG: Type of bitbucket.cloud: {type(bitbucket.cloud)}")
    #     print(f"DEBUG: Is bitbucket.cloud valid? {bool(bitbucket.cloud)}")

    if isinstance(bitbucket, bool) and not bitbucket:
        raise ValueError("Bitbucket client initialization returned a False boolean, likely due to bad credentials.")

except Exception as e:
    print(f"Error initializing Bitbucket client: {e}")
    # Update error message to be more precise for current env vars
    print("Please ensure BITBUCKET_EMAIL, BITBUCKET_APP_PASSWORD, and BITBUCKET_WORKSPACE environment variables are set and correct.")
    exit()

# --- Functions ---

# --- Helper for Paginated API Calls ---
def get_paginated_results(client, path_or_url):
    """Fetches all pages of results from a Bitbucket API endpoint."""
    all_results = []
    current_url = path_or_url
    while current_url:
        try:
            # If path_or_url is a full URL (from 'next' link), use it directly
            # Otherwise, it's a path relative to the base URL
            if current_url.startswith('http'):
                response = client.get(current_url)
            else:
                response = client.get(current_url)

            if isinstance(response, dict) and 'values' in response:
                all_results.extend(response['values'])
                current_url = response.get('next') # URL for the next page
            else:
                # Handle cases where response might not be a dict or lacks 'values'
                print(f"Warning: Unexpected API response format for {path_or_url}: {response}")
                break
        except Exception as e:
            print(f"Error fetching paginated results from {current_url}: {e}")
            break # Stop on error
    return all_results
    
def get_all_projects(workspace):
    """Fetches all projects within a given Bitbucket workspace."""
    print(f"\nFetching projects for workspace: {workspace}...")
    # API path for listing projects in a workspace
    projects_path = f"workspaces/{workspace}/projects"
    projects = get_paginated_results(bitbucket, projects_path)
    print(f"Found {len(projects)} projects.")
    return projects

def get_repositories_for_project(workspace, project_key):
    """Fetches repositories for a specific project within a given Bitbucket workspace."""
    print(f"  Fetching repositories for project: {project_key}...")
    # API path for listing repositories, filtered by project key
    # Note: project.key needs to be enclosed in double quotes in the query string
    repos_path = f"repositories/{workspace}?q=project.key=\"{project_key}\""
    repos = get_paginated_results(bitbucket, repos_path)
    print(f"  Found {len(repos)} repositories for project {project_key}.")
    return repos
    
def get_all_repositories(workspace):
    """Fetches all repositories within a given Bitbucket workspace using a low-level API call."""
    print(f"Fetching repositories for workspace: {workspace}...")
    repos = []
    try:
        # --- CRITICAL FIX: Use bitbucket.get() for direct API call ---
        # The Bitbucket API endpoint for listing repositories is /2.0/repositories/{workspace_slug}
        # This will return a dictionary with a 'values' key containing the list of repositories
        response = bitbucket.get(f"repositories/{workspace}")
        
        if isinstance(response, dict) and 'values' in response:
            repos = response['values']
        else:
            print(f"Warning: Unexpected response format from Bitbucket API: {response}")

        print(f"Found {len(repos)} repositories.")
        return repos
    except Exception as e:
        print(f"Error fetching repositories: {e}")
        return []

def search_terraform_files_in_repo(workspace, repo_slug):
    """
    Searches for Terraform files (.tf, .tfvars) within a repository.
    This uses direct file path checking as Bitbucket's search API is not as granular for content.
    For more robust content search, you'd need to clone the repository or use a more advanced search index.
    """
    terraform_files = []
    try:
        # Define possible Terraform file names and common directories
        possible_tf_files = ['main.tf', 'variables.tf', 'outputs.tf', 'versions.tf', 'providers.tf', 'terraform.tfvars', 'variables.tfvars']
        possible_tf_dirs = ['.', 'terraform', 'infra', 'infrastructure', 'modules', 'environments', 'regions', 'tf'] # Common root and subdirs

        # Get the default branch (usually 'main' or 'master')
        # --- CORRECTED: Use bitbucket.get_repo directly (already done in your code) ---
        repo_details = bitbucket.get_repo(workspace, repo_slug)
        default_branch = repo_details.get('mainbranch', {}).get('name', 'main')
        print(f"  Default branch for {repo_slug}: {default_branch}")

        for directory in possible_tf_dirs:
            for tf_file in possible_tf_files:
                file_path = f"{directory}/{tf_file}" if directory != '.' else tf_file
                try:
                    # Attempt to get the file content
                    # --- CORRECTED: Use bitbucket.get_content_of_file directly (already done in your code) ---
                    content_response = bitbucket.get_content_of_file(
                        workspace=workspace,
                        repo_slug=repo_slug,
                        file_path=file_path,
                        commit_id=default_branch
                    )

                    # Bitbucket API returns file content directly for get_content_of_file
                    if content_response:
                        terraform_files.append({
                            'repo_name': repo_slug,
                            'file_path': file_path,
                            'content': content_response.decode('utf-8') # Decode bytes to string
                        })
                except Exception as file_error:
                    # File not found or other error, continue to next file
                    pass
    except Exception as e:
        print(f"Error searching Terraform files in {repo_slug}: {e}")

    return terraform_files


def analyze_terraform_content(file_content):
    """Analyzes Terraform file content for boilerplate indicators and module definitions."""
    analysis_results = {
        'is_terraform': False,
        'has_modules': False,
        'is_boilerplate_candidate': False,
        'module_sources': [],
        'resource_count': 0,
        'variable_count': 0,
        'output_count': 0
    }

    # Simple check for common Terraform syntax
    if re.search(r'(resource|variable|output|data|provider) "[^"]+"', file_content):
        analysis_results['is_terraform'] = True

    # Check for module declarations
    module_matches = re.findall(r'module\s+"[^"]+"\s*{\s*source\s*=\s*"([^"]+)"', file_content)
    if module_matches:
        analysis_results['has_modules'] = True
        analysis_results['module_sources'].extend(module_matches)

    # Check for boilerplate keywords within comments or general text
    for keyword in BOILERPLATE_KEYWORDS:
        if keyword in file_content.lower():
            analysis_results['is_boilerplate_candidate'] = True
            break

    # Count basic Terraform blocks (can be refined with HCL parsing)
    analysis_results['resource_count'] = len(re.findall(r'resource\s+"[^"]+"', file_content))
    analysis_results['variable_count'] = len(re.findall(r'variable\s+"[^"]+"', file_content))
    analysis_results['output_count'] = len(re.findall(r'output\s+"[^"]+"', file_content))

    return analysis_results

def main():
    global bitbucket # Ensure we're using the global bitbucket variable

    if not BITBUCKET_EMAIL:
        print("ERROR: BITBUCKET_EMAIL environment variable not set.")
        exit()
    if not BITBUCKET_APP_PASSWORD:
        print("ERROR: BITBUCKET_APP_PASSWORD environment variable not set.")
        exit()
    if not BITBUCKET_WORKSPACE:
        print("ERROR: BITBUCKET_WORKSPACE environment variable not set or has a typo.")
        print("Expected variable name: BITBUCKET_WORKSPACE")
        exit()

    if not isinstance(bitbucket, Cloud):
        print("FATAL ERROR: BitbucketCloud client could not be initialized correctly. Exiting.")
        exit()

    all_boilerplate_candidates = [] # Renamed to avoid confusion with per-repo list

    # --- NEW APPROACH START ---
    projects = get_all_projects(BITBUCKET_WORKSPACE)

    for project in projects:
        project_key = project.get('key')
        project_name = project.get('name')
        if not project_key:
            print(f"Skipping project due to missing key: {project}")
            continue
        
        print(f"\nProcessing project: {project_name} ({project_key})")
        
        repositories = get_repositories_for_project(BITBUCKET_WORKSPACE, project_key)

        for repo in repositories:
            repo_slug = repo.get('slug')
            if not repo_slug:
                print(f"Skipping repository due to missing slug: {repo}")
                continue

            print(f"\n  Processing repository: {repo_slug} in project {project_key}")
            
            if any(keyword in repo_slug.lower() for keyword in BOILERPLATE_KEYWORDS):
                print(f"    Repo name suggests boilerplate: {repo_slug}")

            terraform_files_in_repo = search_terraform_files_in_repo(BITBUCKET_WORKSPACE, repo_slug)

            for tf_file in terraform_files_in_repo:
                file_path = tf_file['file_path']
                content = tf_file['content']
                
                if not file_path.endswith(TERRAFORM_FILE_EXTENSIONS):
                    continue

                analysis = analyze_terraform_content(content)

                if analysis['is_terraform']:
                    print(f"    Found Terraform file: {file_path}")
                    if analysis['is_boilerplate_candidate'] or (analysis['has_modules'] and analysis['resource_count'] > 0):
                        all_boilerplate_candidates.append({ # Append to the overall list
                            'project_key': project_key, # Add project context
                            'project_name': project_name,
                            'repo_name': repo_slug,
                            'file_path': file_path,
                            'analysis': analysis
                        })
                        print(f"    Potential boilerplate candidate due to: "
                              f"Boilerplate Keywords: {analysis['is_boilerplate_candidate']}, "
                              f"Has Modules: {analysis['has_modules']}, "
                              f"Resource Count: {analysis['resource_count']}")
                    elif analysis['has_modules']:
                        print(f"    Contains modules: {analysis['module_sources']}")
    # --- NEW APPROACH END ---

    print("\n--- Summary of Potential Terraform Boilerplate Candidates ---")
    if not all_boilerplate_candidates:
        print("No potential boilerplate candidates found based on the criteria.")
    else:
        for candidate in all_boilerplate_candidates:
            print(f"\nProject: {candidate['project_name']} ({candidate['project_key']})") # Include project info
            print(f"Repository: {candidate['repo_name']}")
            print(f"  File: {candidate['file_path']}")
            print(f"  Analysis:")
            for key, value in candidate['analysis'].items():
                print(f"    {key}: {value}")
            print("-" * 30)

if __name__ == "__main__":
    main()