import os
import re
import sys
import yaml

def find_values_file(chart_path):
    """
    Finds the values file in a Helm chart directory, accommodating different naming conventions.
    """
    possible_names = ['values.yaml', 'values.yml', 'values-prod.yaml', 'values-prod.yml', 'values-st.yaml', 'values-st.yml']
    for name in possible_names:
        file_path = os.path.join(chart_path, name)
        if os.path.exists(file_path):
            return file_path
    return None

def validate_helm_chart(chart_path):
    """
    Validates a Helm chart for security and best-practice issues.
    Returns a dictionary of validation results.
    """
    chart_name = os.path.basename(chart_path)
    results = {
        'type': 'Helm Chart',
        'path': chart_path,
        'name': chart_name,
        'status': 'PASS',
        'messages': [],
        'parsing_errors': []
    }
    sensitive_keys = ['password', 'secret', 'token', 'api_key', 'access_key', 'license_key', 'password_hash']

    values_path = find_values_file(chart_path)
    if values_path:
        try:
            with open(values_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for key in sensitive_keys:
                    match = re.search(f'^{key}:\\s*(.+)$', content, re.MULTILINE | re.IGNORECASE)
                    if match and match.group(1).strip() != '""' and not match.group(1).strip().startswith(('{{', '"{{')):
                        results['status'] = 'FAIL'
                        results['messages'].append(f"❌ Found potential hardcoded secret in {values_path} for key: '{key}'")
        except yaml.YAMLError as e:
            results['status'] = 'FAIL'
            results['messages'].append(f"ERROR: Failed to parse {values_path}: {e}")
            results['parsing_errors'].append({
                'filename': os.path.basename(values_path),
                'root_cause': getattr(e, 'problem', 'Unknown parsing error.'),
                'line': getattr(getattr(e, 'context_mark', None), 'line', 'N/A'),
                'column': getattr(getattr(e, 'context_mark', None), 'column', 'N/A'),
                'message': str(e)
            })
    else:
        results['messages'].append("INFO: No values file found. Skipping checks.")

    templates_path = os.path.join(chart_path, 'templates')
    if os.path.exists(templates_path):
        for root, _, files in os.walk(templates_path):
            for file in files:
                if file.endswith(('.yaml', '.yml')):
                    manifest_path = os.path.join(root, file)
                    try:
                        with open(manifest_path, 'r', encoding='utf-8') as f:
                            manifests = list(yaml.safe_load_all(f))
                            for manifest in manifests:
                                if manifest is None: continue
                                
                                if manifest.get('kind') == 'Secret' and 'data' in manifest:
                                    for key, value in manifest['data'].items():
                                        if isinstance(value, str) and (' ' in value or '\n' in value):
                                            results['status'] = 'FAIL'
                                            results['messages'].append(f"❌ Insecure secret in {manifest_path}. 'data' field should be Base64 encoded.")
                                
                                if manifest.get('kind') in ['Deployment', 'StatefulSet', 'DaemonSet']:
                                    containers = manifest.get('spec', {}).get('template', {}).get('spec', {}).get('containers', [])
                                    for container in containers:
                                        if 'env' in container:
                                            for env_var in container['env']:
                                                if 'value' in env_var:
                                                    value = str(env_var['value']).lower()
                                                    for key in sensitive_keys:
                                                        if key in value and not value.startswith(('{{', '"{{')):
                                                            results['status'] = 'FAIL'
                                                            results['messages'].append(f"❌ Found potential hardcoded secret in {manifest_path} for env var '{env_var.get('name')}'.")
                    except yaml.YAMLError as e:
                        results['status'] = 'FAIL'
                        results['messages'].append(f"❌ Failed to parse manifest {manifest_path}")
                        results['parsing_errors'].append({
                            'filename': os.path.basename(manifest_path),
                            'root_cause': getattr(e, 'problem', 'Unknown parsing error.'),
                            'line': getattr(getattr(e, 'context_mark', None), 'line', 'N/A'),
                            'column': getattr(getattr(e, 'context_mark', None), 'column', 'N/A'),
                            'message': str(e)
                        })
    
    if not any('❌' in msg for msg in results['messages']) and not results['parsing_errors']:
        results['messages'].insert(0, "✅ All basic checks passed.")
        results['status'] = 'PASS'
    else:
        results['status'] = 'FAIL'
    return results

def lint_buildspec_file(file_path):
    """
    Lints a buildspec.yaml file and returns a dictionary of validation results.
    """
    results = {
        'type': 'Buildspec',
        'path': file_path,
        'name': os.path.basename(file_path),
        'status': 'PASS',
        'messages': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            buildspec_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        results['status'] = 'FAIL'
        results['messages'].append(f"❌ ERROR: Failed to parse YAML syntax: {e}")
        return results
    except Exception as e:
        results['status'] = 'FAIL'
        results['messages'].append(f"❌ ERROR: Failed to read file: {e}")
        return results

    if 'version' not in buildspec_data:
        results['status'] = 'FAIL'
        results['messages'].append("❌ ERROR: Missing required 'version' field.")
    
    if 'phases' not in buildspec_data:
        results['status'] = 'FAIL'
        results['messages'].append("❌ ERROR: Missing 'phases' section.")
    else:
        phases = buildspec_data['phases']
        if 'install' in phases:
            results['messages'].append("✅ Found 'install' phase. Good practice for dependencies.")
        if 'pre_build' in phases:
            results['messages'].append("✅ Found 'pre_build' phase. Useful for pre-build checks.")
        if 'build' in phases:
            results['messages'].append("✅ Found 'build' phase. This is where your core build commands belong.")
        if 'post_build' in phases:
            results['messages'].append("✅ Found 'post_build' phase. Ideal for testing, tagging, and deployments.")
        if not any(p in phases for p in ['install', 'pre_build', 'build', 'post_build']):
            results['messages'].append("⚠️ WARNING: No common build phases found. The build may not have clear stages.")
    
    env_data = buildspec_data.get('env', {})
    if 'variables' in env_data:
        results['messages'].append("✅ Found 'variables' section.")
        for name, value in env_data['variables'].items():
            if any(key in name.lower() for key in ['secret', 'password', 'token', 'key']):
                results['status'] = 'FAIL'
                results['messages'].append(f"❌ ERROR: Potential hardcoded secret found in variable '{name}'. Use the 'secrets-manager' section instead.")
    
    secrets_data = env_data.get('secrets-manager', {})
    if secrets_data:
        results['messages'].append("✅ Found 'secrets-manager' section. Great for secure credential management.")
        for var_name, secret_arn_value in secrets_data.items():
            if ':' not in secret_arn_value:
                results['status'] = 'FAIL'
                results['messages'].append(f"❌ ERROR: Secrets Manager value for '{var_name}' should be in the format 'secret-name:json-key' or 'secret-id'.")
            elif not secret_arn_value.endswith((':', '*')):
                results['messages'].append(f"⚠️ WARNING: The ARN for secret '{var_name}' does not end in a wildcard or a colon. This may not retrieve the latest version.")
    else:
        results['messages'].append("⚠️ WARNING: No 'secrets-manager' section found. Consider using it for sensitive environment variables.")
        
    if results['status'] == 'PASS':
        results['messages'].insert(0, "✅ All basic checks passed. Buildspec looks good.")

    return results

def generate_html_report(helm_results, buildspec_results, output_file):
    """
    Generates an HTML report from validation results for both Helm and Buildspec files.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Pipeline Validation Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            .report-section { margin-top: 40px; }
            .report-container { border: 1px solid #ccc; border-radius: 8px; padding: 20px; margin-top: 20px; }
            .file-header { display: flex; align-items: center; justify-content: space-between; padding: 10px; font-weight: bold; border-bottom: 1px solid #eee; }
            .status-pass { color: green; }
            .status-fail { color: red; }
            .messages { list-style-type: none; padding: 0; }
            .messages li { padding: 5px 0; border-bottom: 1px solid #f0f0f0; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .error-table-container { margin-top: 20px; }
            .empty-report { text-align: center; color: #555; }
        </style>
    </head>
    <body>
        <h1>Pipeline Validation Report</h1>
        <div class="report-section">
            <h2>Helm Chart Validation</h2>
    """
    if not helm_results:
        html_content += """
        <p class="empty-report">No Helm charts found in the specified directory.</p>
        """
    for result in helm_results:
        status_class = "status-pass" if result['status'] == "PASS" else "status-fail"
        status_symbol = "✅" if result['status'] == "PASS" else "❌"
        
        html_content += f"""
        <div class="report-container">
            <div class="file-header">
                <span>Chart: {result['name']}</span>
                <span class="{status_class}">{status_symbol} {result['status']}</span>
            </div>
            <ul class="messages">
                {''.join(f'<li>{msg}</li>' for msg in result['messages'])}
            </ul>
        """
        
        if result['parsing_errors']:
            html_content += """
            <div class="error-table-container">
                <h3>YAML Parsing Errors</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Filename</th>
                            <th>Error Root Cause</th>
                            <th>Line</th>
                            <th>Column</th>
                            <th>Error</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            for error in result['parsing_errors']:
                html_content += f"""
                        <tr>
                            <td>{error['filename']}</td>
                            <td>{error['root_cause']}</td>
                            <td>{error['line']}</td>
                            <td>{error['column']}</td>
                            <td>{error['message']}</td>
                        </tr>
                """
            html_content += """
                    </tbody>
                </table>
            </div>
            """
        html_content += """
        </div>
        """
    
    html_content += """
        </div>
        <div class="report-section">
            <h2>Buildspec Validation</h2>
    """
    if not buildspec_results:
        html_content += """
        <p class="empty-report">No buildspec files found in the specified directory.</p>
        """
    for result in buildspec_results:
        status_class = "status-pass" if result['status'] == "PASS" else "status-fail"
        status_symbol = "✅" if result['status'] == "PASS" else "❌"
        
        html_content += f"""
        <div class="report-container">
            <div class="file-header">
                <span>Buildspec File: {result['name']}</span>
                <span class="{status_class}">{status_symbol} {result['status']}</span>
            </div>
            <ul class="messages">
                {''.join(f'<li>{msg}</li>' for msg in result['messages'])}
            </ul>
        </div>
        """
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_pipeline.py <path_to_directory>")
        sys.exit(1)

    root_dir = sys.argv[1]
    if not os.path.isdir(root_dir):
        print(f"ERROR: Directory not found at '{root_dir}'")
        sys.exit(1)
        
    helm_results = []
    buildspec_results = []
    
    buildspec_names = ['helm-deploy-prod.yaml', 'helm-deploy-prod.yml', 
                       'helm-deploy-st.yaml', 'helm-deploy-st.yml', 
                       'buildspec.yaml', 'buildspec.yml', 
                       'buildspec-st.yaml', 'buildspec-st.yml']
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if 'Chart.yaml' in filenames:
            helm_result = validate_helm_chart(dirpath)
            helm_results.append(helm_result)
        
        for filename in filenames:
            if filename in buildspec_names:
                buildspec_result = lint_buildspec_file(os.path.join(dirpath, filename))
                buildspec_results.append(buildspec_result)
    
    report_name = "helm_VLinter_Report.html"
    generate_html_report(helm_results, buildspec_results, report_name)
    print(f"\nValidation complete. Report generated at {report_name}")
    
    if helm_results or buildspec_results:
        if any(r['status'] == 'FAIL' for r in helm_results) or any(r['status'] == 'FAIL' for r in buildspec_results):
            sys.exit(1)
    else:
        print(f"No Helm charts or buildspec files found in '{root_dir}'.")
        sys.exit(1)

if __name__ == "__main__":
    main()