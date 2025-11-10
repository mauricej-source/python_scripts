import os
from atlassian import Bitbucket

print("--- Starting Bitbucket Client Introspection ---")

# --- Configuration (ensure environment variables are set as before) ---
BITBUCKET_USERNAME = os.environ.get("BITBUCKET_USERNAME")
BITBUCKET_APP_PASSWORD = os.environ.get("BITBUCKET_APP_PASSWORD")
BITBUCKET_WORKSPACE = os.environ.get("BITBUCKET_WORKSPACE")

if not BITBUCKET_USERNAME or not BITBUCKET_APP_PASSWORD or not BITBUCKET_WORKSPACE:
    print("ERROR: Please ensure BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD, and BITBUCKET_WORKSPACE environment variables are set.")
    exit()

# --- Bitbucket API Client Initialization ---
bitbucket = None
try:
    bitbucket = Bitbucket(
        url='https://api.bitbucket.org/',
        username='insertUserNameHere',
        password='insertPasswordHere',
        cloud=True
    )
	
    print(f"\nDEBUG: Bitbucket client object created. Type: {type(bitbucket)}")
    print(f"DEBUG: Is bitbucket object valid? {bool(bitbucket)}")

    # --- Inspecting bitbucket.cloud attribute ---
    print("\n--- Inspecting bitbucket.cloud ---")
    if hasattr(bitbucket, 'cloud'):
        if isinstance(bitbucket.cloud, bool):
            print(f"  bitbucket.cloud is a boolean: {bitbucket.cloud}")
        else:
            print(f"  Type of bitbucket.cloud: {type(bitbucket.cloud)}")
            print(f"  Is bitbucket.cloud valid? {bool(bitbucket.cloud)}")
            print("  Attempting to list attributes of bitbucket.cloud (if it's an object):")
            try:
                for attr_name in sorted(dir(bitbucket.cloud)):
                    if not attr_name.startswith('_'): # Skip private/dunder methods
                        attr = getattr(bitbucket.cloud, attr_name)
                        print(f"    .cloud.{attr_name}: {type(attr)}")
            except Exception as e:
                print(f"  Could not inspect bitbucket.cloud attributes: {e}")
    else:
        print("  bitbucket object has no 'cloud' attribute.")

    # --- Inspecting bitbucket.repositories attribute ---
    print("\n--- Inspecting bitbucket.repositories ---")
    if hasattr(bitbucket, 'repositories'):
        attr = getattr(bitbucket, 'repositories')
        print(f"  Type of bitbucket.repositories: {type(attr)}")
        if callable(attr): # If it's a direct method like bitbucket.repositories()
            print(f"  bitbucket.repositories is callable (might be a direct method).")
        else: # If it's an object/sub-client like bitbucket.repositories.each()
            print("  Attempting to list attributes of bitbucket.repositories (if it's an object):")
            try:
                for attr_name in sorted(dir(attr)):
                    if not attr_name.startswith('_'):
                        sub_attr = getattr(attr, attr_name)
                        print(f"    .repositories.{attr_name}: {type(sub_attr)}")
            except Exception as e:
                print(f"  Could not inspect bitbucket.repositories attributes: {e}")
    else:
        print("  bitbucket object has no 'repositories' attribute.")

    # --- Listing All Top-Level Attributes of Bitbucket Object ---
    print("\n--- All Top-Level Attributes of Bitbucket Object ---")
    found_methods = []
    found_subclients = []
    for attr_name in sorted(dir(bitbucket)):
        if not attr_name.startswith('_'): # Skip private/dunder methods
            attr = getattr(bitbucket, attr_name)
            if callable(attr):
                found_methods.append(attr_name)
            elif not isinstance(attr, (int, float, str, bool, list, dict, set, tuple, type(None))): # If it's another complex object (likely a sub-client)
                found_subclients.append(attr_name)
            # print(f"  {attr_name}: {type(attr)}") # More verbose if needed

    if found_methods:
        print("Callable methods directly on bitbucket object:")
        for method in found_methods:
            print(f"  - {method}")
    else:
        print("No direct callable methods found on bitbucket object (unusual).")

    if found_subclients:
        print("\nSub-clients/objects directly on bitbucket object:")
        for subclient in found_subclients:
            print(f"  - {subclient} (type: {type(getattr(bitbucket, subclient))})")
    else:
        print("No direct sub-clients/objects found on bitbucket object (unusual).")

except Exception as e:
    print(f"\nERROR: During Bitbucket client initialization or introspection: {e}")
    print("Please ensure BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD environment variables are set and correct.")
    exit()

print("\n--- End Bitbucket Client Introspection ---")
print("This script completed its introspection. No further API calls were attempted.")