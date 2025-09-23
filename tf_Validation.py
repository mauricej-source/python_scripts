import hcl2
import json
import os
import re
import sys

def validate_terraform_file(tf_file_path):
    """
    Parses a Terraform file and validates specific AWS resource configurations.
    Returns a dictionary of validation results.
    """
    results = {
        'file_path': tf_file_path,
        'status': 'PASS',
        'messages': []
    }
    
    try:
        with open(tf_file_path, 'r', encoding='utf-8') as f:
            terraform_data = hcl2.load(f)
    except FileNotFoundError:
        results['status'] = 'FAIL'
        results['messages'].append(f"ERROR: File not found at '{tf_file_path}'")
        return results
    except Exception as e:
        results['status'] = 'FAIL'
        results['messages'].append(f"ERROR: Failed to parse HCL file: {e}")
        return results

    # 1. Validate IAM Role Policy Permissions
    iam_policy_found = False
    for resource in terraform_data.get('resource', []):
        if 'aws_iam_role_policy' in resource:
            iam_policy_found = True
            policy_resource = resource['aws_iam_role_policy']
            policy_name = list(policy_resource.keys())[0]
            policy_doc_str = policy_resource[policy_name].get('policy', '""')

            try:
                policy_doc = json.loads(policy_doc_str.replace('\n', ''))
            except json.JSONDecodeError:
                results['messages'].append("WARNING: Could not parse IAM policy JSON. Skipping policy validation.")
                continue

            secrets_perm_ok = False
            for statement in policy_doc.get('Statement', []):
                actions = statement.get('Action', [])
                resources = statement.get('Resource', [])
                if 'secretsmanager:GetSecretValue' in actions and 'arn:aws:secretsmanager:us-east-1:050853773894:secret:leads-profile-secrets-st*' in resources:
                    secrets_perm_ok = True
                    break
            
            if secrets_perm_ok:
                results['messages'].append("✅ IAM Policy has correct secretsmanager:GetSecretValue permissions.")
            else:
                results['status'] = 'FAIL'
                results['messages'].append("❌ IAM Policy is missing correct secretsmanager permissions.")

    if not iam_policy_found:
        results['messages'].append("INFO: No aws_iam_role_policy resource found in the file. Skipping.")

    # 2. Validate CodeBuild Project Secrets Configuration
    codebuild_project_found = False
    for resource in terraform_data.get('resource', []):
        if 'aws_codebuild_project' in resource:
            codebuild_project_found = True
            project_resource = resource['aws_codebuild_project']
            project_name = list(project_resource.keys())[0]
            env_vars = project_resource[project_name].get('environment', {}).get('environment_variable', [])

            secrets_env_ok = False
            for var in env_vars:
                if var.get('name') == 'newrelic_st_license' and var.get('type') == 'SECRETS_MANAGER' and var.get('value') == 'leads-profile-secrets-st:newrelic_st_license':
                    secrets_env_ok = True
                    break
            
            if secrets_env_ok:
                results['messages'].append("✅ CodeBuild project is configured correctly for secrets.")
            else:
                results['status'] = 'FAIL'
                results['messages'].append("❌ CodeBuild project secrets configuration is incorrect.")

    if not codebuild_project_found:
        results['messages'].append("INFO: No aws_codebuild_project resource found in the file. Skipping.")

    # 3. Check for Hardcoded Secrets
    try:
        with open(tf_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            hardcoded_secrets = re.findall(r'(password|key|token|secret)[ =:"\'][^"\s]{8,}', content, re.IGNORECASE)
            
            if hardcoded_secrets:
                results['status'] = 'FAIL'
                results['messages'].append(f"❌ Found potential hardcoded secrets: {hardcoded_secrets}")
            else:
                results['messages'].append("✅ No obvious hardcoded secrets found.")
    except Exception as e:
        results['messages'].append(f"WARNING: Could not scan file for hardcoded secrets: {e}")

    return results

def generate_html_report(validation_results, output_file):
    """
    Generates an HTML report from the validation results.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Terraform Validation Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            .report-container { border: 1px solid #ccc; border-radius: 8px; padding: 20px; margin-top: 20px; }
            .file-header { display: flex; align-items: center; justify-content: space-between; padding: 10px; font-weight: bold; border-bottom: 1px solid #eee; }
            .status-pass { color: green; }
            .status-fail { color: red; }
            .messages { list-style-type: none; padding: 0; }
            .messages li { padding: 5px 0; border-bottom: 1px solid #f0f0f0; }
        </style>
    </head>
    <body>
        <h1>Terraform Validation Report</h1>
    """

    for result in validation_results:
        status_class = "status-pass" if result['status'] == "PASS" else "status-fail"
        status_symbol = "✅" if result['status'] == "PASS" else "❌"
        
        html_content += f"""
        <div class="report-container">
            <div class="file-header">
                <span>File: {result['file_path']}</span>
                <span class="{status_class}">{status_symbol} {result['status']}</span>
            </div>
            <ul class="messages">
                {''.join(f'<li>{msg}</li>' for msg in result['messages'])}
            </ul>
        </div>
        """

    html_content += """
    </body>
    </html>
    """
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_tf.py <path_to_terraform_directory>")
        sys.exit(1)
    
    root_directory = sys.argv[1]
    validation_results = []
    
    print(f"Scanning directory: {root_directory} for '.tf' files...")
    
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            if filename.endswith('.tf'):
                file_path = os.path.join(dirpath, filename)
                result = validate_terraform_file(file_path)
                validation_results.append(result)
                
    report_name = "tf_ValidationReport.html"
    generate_html_report(validation_results, report_name)
    print(f"\nValidation complete. Report generated at {report_name}")

if __name__ == "__main__":
    main()