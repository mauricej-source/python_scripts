import os
import sys
import re
from jinja2 import Environment, FileSystemLoader

def find_tf_files(start_path):
    """Recursively finds all .tf and .tfvars files in a given directory."""
    tf_files = []
    for root, _, files in os.walk(start_path):
        for file in files:
            if file.endswith(('.tf', '.tfvars')):
                tf_files.append(os.path.join(root, file))
    return tf_files

def analyze_tf_files(tf_files):
    """
    Reads each file and returns a list of dictionaries with 'variable' and 'arn' keys.
    """
    roles = []
    
    for file_path in tf_files:
        try:
            with open(file_path, 'r', encoding='utf8') as f:
                for line in f:
                    stripped_line = line.strip()
                    if "role" in stripped_line and "=" in stripped_line and "arn:aws:iam" in stripped_line and "spacelift" not in stripped_line:
                        parts = stripped_line.split('=', 1)
                        if len(parts) == 2:
                            variable_name = parts[0].strip()
                            arn_value = parts[1].strip()
                            roles.append({
                                "variable": variable_name,
                                "arn": arn_value
                            })
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    return roles

def generate_report(roles_data):
    """
    Generates the HTML report by building the string directly from the roles_data.
    """
    # Remove duplicates by converting the list of dictionaries to a set of tuples
    unique_roles_tuples = {tuple(sorted(d.items())) for d in roles_data}
    unique_roles = [dict(t) for t in unique_roles_tuples]
    
    # Sort the roles for a consistent report
    unique_roles.sort(key=lambda x: (x['variable'], x['arn']))

    # --- Start of direct HTML string generation ---
    
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terraform Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f9; color: #333; }
        .container { max-width: 900px; margin: auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }
        h1, h2 { color: #0056b3; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { text-align: left; padding: 12px; border-bottom: 1px solid #ddd; }
        th { background-color: #e2eafc; }
        tr:hover { background-color: #f1f1f1; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Terraform Analysis Report</h1>
        <p>This report lists all unique roles found in your Terraform files.</p>
        
        <h2>Roles</h2>
"""

    if unique_roles:
        html_content += """
        <table>
            <thead>
                <tr>
                    <th>Role Variable</th>
                    <th>Role ARN</th>
                </tr>
            </thead>
            <tbody>
"""
        for role in unique_roles:
            html_content += f"""
                <tr>
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
    # --- End of direct HTML string generation ---

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

    tf_files = find_tf_files(start_directory)
    roles = analyze_tf_files(tf_files)
    generate_report(roles)