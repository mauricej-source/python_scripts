import os
import sys
import re

def find_tf_files(start_path):
    """
    Recursively finds all .tf and .tfvars files in a given directory,
    while avoiding specific subdirectories.
    """
    tf_files = []
    excluded_dirs = ['cloud_formation', 'modules', 'functions']
    
    for root, dirs, files in os.walk(start_path):
        # Modify the list of directories in-place to prevent os.walk from entering them
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        
        for file in files:
            if file.endswith(('.tf', '.tfvars')):
                file_path = os.path.join(root, file)
                tf_files.append(file_path)
                            
    return list(set(tf_files)) # Return a unique list

def analyze_tf_files(tf_files):
    """
    Reads each file and returns a dictionary with lists for roles, AWS resources, and modules.
    """
    roles = []
    aws_resources = []
    modules = []

    # Regex for a resource block, capturing the resource type and the resource name
    resource_pattern = re.compile(r'^\s*resource\s+"(aws_[^"]+)"\s+"([^"]+)"')
    
    # Regex to capture module block declarations
    module_block_pattern = re.compile(r'^\s*module\s+"([^"]+)"\s*\{')

    # Regex for variables within a module block
    source_pattern = re.compile(r'^\s*source\s*=\s*"(?:\.\/)?([^"]+)"')
    app_name_pattern = re.compile(r'^\s*app_name\s*=\s*"(?:\.\/)?([^"]+)"')
    
    # Regex for a generic 'name' variable
    name_pattern = re.compile(r'^\s*name\s*=\s*"(?:\.\/)?([^"]+)"')

    for file_path in tf_files:
        try:
            with open(file_path, 'r', encoding='utf8') as f:
                in_module_block = False
                current_module = {}
                last_resource_info = None
                
                for line in f:
                    stripped_line = line.strip()
                    
                    # If we just saw a resource line, check the current line for a 'name' variable
                    if last_resource_info:
                        name_match = name_pattern.search(stripped_line)
                        if name_match:
                            last_resource_info["resource_name"] = name_match.group(1)
                        aws_resources.append(last_resource_info)
                        last_resource_info = None

                    # Check for start of a new module block
                    module_block_match = module_block_pattern.search(stripped_line)
                    if module_block_match:
                        in_module_block = True
                        current_module = {"name": module_block_match.group(1)}
                        continue
                    
                    # Check for end of a module block
                    if in_module_block and stripped_line == '}':
                        modules.append(current_module)
                        in_module_block = False
                        current_module = {}
                        continue

                    # If inside a module block, look for source and app_name
                    if in_module_block:
                        source_match = source_pattern.search(stripped_line)
                        if source_match:
                            current_module["source"] = source_match.group(1)
                            
                        app_name_match = app_name_pattern.search(stripped_line)
                        if app_name_match:
                            current_module["app_name"] = app_name_match.group(1)
                    
                    # Check for a new AWS resource declaration
                    resource_match = resource_pattern.search(stripped_line)
                    if resource_match:
                        last_resource_info = {
                            "resource_type": resource_match.group(1),
                            "resource_name": resource_match.group(2)
                        }

                    # Check for role assignments (original logic, independent of blocks)
                    if "role" in stripped_line and "=" in stripped_line and "arn:aws:iam" in stripped_line and "spacelift" not in stripped_line:
                        parts = stripped_line.split('=', 1)
                        if len(parts) == 2:
                            variable_name = parts[0].strip()
                            arn_value = parts[1].strip()
                            roles.append({
                                "variable": variable_name,
                                "arn": arn_value
                            })
            
            # Append any trailing resource info if the file ends on a resource line
            if last_resource_info:
                aws_resources.append(last_resource_info)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    return {"roles": roles, "resources": aws_resources, "modules": modules}

def generate_report(report_data):
    """
    Generates the HTML report by building the string directly from the report_data.
    """
    roles_data = report_data["roles"]
    resources_data = report_data["resources"]
    modules_data = report_data["modules"]
    
    # Process roles data and add source column
    # Map of account numbers to environment names
    env_map = {
        '050853773894': 'MGMT',
        '363145861140': 'NONProd',
        '324765430599': 'PROD'
    }
    
    # Add a 'source' key to each role dictionary
    for role in roles_data:
        arn_parts = role['arn'].split(':')
        account_number = arn_parts[4] if len(arn_parts) > 4 else None
        role['source'] = env_map.get(account_number, 'Unknown')

    unique_roles_tuples = {tuple(sorted(d.items())) for d in roles_data}
    unique_roles = [dict(t) for t in unique_roles_tuples]
    unique_roles.sort(key=lambda x: (x['source'], x['variable'], x['arn']))
    
    # Process AWS resources data
    unique_resources_tuples = {tuple(sorted(d.items())) for d in resources_data}
    unique_resources = [dict(t) for t in unique_resources_tuples]
    unique_resources.sort(key=lambda x: x['resource_type'])
    
    # Process modules data
    unique_modules_tuples = {tuple(sorted(d.items())) for d in modules_data if 'app_name' in d and 'source' in d}
    unique_modules = [dict(t) for t in unique_modules_tuples]
    unique_modules.sort(key=lambda x: (x['app_name'], x['source']))
    
    # --- Start of direct HTML string generation ---
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terraform Analysis Report</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background-color: #f4f4f9; 
            color: #333; 
            font-size: 14px;
        }
        .container { 
            max-width: 900px; 
            margin: auto; 
            background: #fff; 
            padding: 20px; 
            border-radius: 8px; 
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); 
        }
        h1, h2 { 
            color: #0056b3; 
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 20px; 
        }
        th, td { 
            text-align: left; 
            padding: 12px; 
            border-bottom: 1px solid #ddd;
            font-size: 12px;
        }
        th { 
            background-color: #e2eafc; 
        }
        tr:hover { 
            background-color: #f1f1f1; 
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Terraform Analysis Report</h1>
        <p>This report lists all unique AWS resources and roles found in your Terraform files.</p>
"""
    # --- Modules Section ---
    html_content += """
        <h2>Modules Used</h2>
"""
    if unique_modules:
        html_content += """
        <table>
            <thead>
                <tr>
                    <th>Application Name</th>
                    <th>Module Source</th>
                </tr>
            </thead>
            <tbody>
"""
        for module in unique_modules:
            html_content += f"""
                <tr>
                    <td><code>{module.get('app_name', 'N/A')}</code></td>
                    <td><code>{module.get('source', 'N/A')}</code></td>
                </tr>
"""
        html_content += """
            </tbody>
        </table>
"""
    else:
        html_content += """
        <p>No modules were found in the specified Terraform files.</p>
"""
    
    # --- AWS Resources Section ---
    html_content += """
        <h2>AWS Resources</h2>
"""
    if unique_resources:
        html_content += """
        <table>
            <thead>
                <tr>
                    <th>Resource Type</th>
                    <th>Resource Name</th>
                </tr>
            </thead>
            <tbody>
"""
        for resource in unique_resources:
            html_content += f"""
                <tr>
                    <td><code>{resource['resource_type']}</code></td>
                    <td><code>{resource['resource_name']}</code></td>
                </tr>
"""
        html_content += """
            </tbody>
        </table>
"""
    else:
        html_content += """
        <p>No AWS resources were found in the specified Terraform files.</p>
"""

    # --- Roles Section ---
    html_content += """
        <h2>Roles</h2>
"""
    if unique_roles:
        html_content += """
        <table>
            <thead>
                <tr>
                    <th>Source</th>
                    <th>Role Variable</th>
                    <th>Role ARN</th>
                </tr>
            </thead>
            <tbody>
"""
        for role in unique_roles:
            html_content += f"""
                <tr>
                    <td><code>{role.get('source', 'N/A')}</code></td>
                    <td><code>{role['variable']}</code></td>
                    <td><code>{role['arn']}</code></td>
                </tr>
"""
        html_content += """
            </tbody>
        </table>
"""
    else:
        html_content += """
        <p>No roles were found in the specified Terraform files.</p>
"""

    html_content += """
    </div>
</body>
</html>
"""
    
    with open('tf_Analysis_Report.html', 'w', encoding='utf8') as f:
        f.write(html_content)
    print("Report generated successfully: tf_Analysis_Report.html")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tf_analysis.py <start_directory>")
        sys.exit(1)

    start_directory = sys.argv[1]
    if not os.path.isdir(start_directory):
        print(f"Error: The directory '{start_directory}' does not exist.")
        sys.exit(1)

    report_data = analyze_tf_files(find_tf_files(start_directory))
    generate_report(report_data)