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
        'chart_path': chart_path,
        'chart_name': chart_name,
        'status': 'PASS',
        'messages': [],
        'parsing_errors': []
    }
    sensitive_keys = ['password', 'secret', 'token', 'api_key', 'access_key', 'license_key', 'password_hash']

    # --- Check for hardcoded secrets in values.yaml ---
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

    # --- Check manifest templates for insecure secret usage ---
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
                                if manifest is None:
                                    continue
                                
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

def generate_html_report(validation_results, output_file):
    """
    Generates an HTML report from the validation results.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Helm Validation Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
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
        </style>
    </head>
    <body>
        <h1>Helm Chart Validation Report</h1>
    """

    for result in validation_results:
        status_class = "status-pass" if result['status'] == "PASS" else "status-fail"
        status_symbol = "✅" if result['status'] == "PASS" else "❌"
        
        html_content += f"""
        <div class="report-container">
            <div class="file-header">
                <span>Chart: {result['chart_name']}</span>
                <span class="{status_class}">{status_symbol} {result['status']}</span>
            </div>
            <ul class="messages">
                {''.join(f'<li>{msg}</li>' for msg in result['messages'])}
            </ul>
        """
        
        # Add the table for parsing errors
        if result['parsing_errors']:
            html_content += """
            <div class="error-table-container">
                <h3>YAML Parsing Errors</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Error</th>
                            <th>Filename</th>
                            <th>Root Cause</th>
                            <th>Line</th>
                            <th>Column</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            for error in result['parsing_errors']:
                html_content += f"""
                        <tr>
                            <td>{error['message']}</td>
                            <td>{error['filename']}</td>
                            <td>{error['root_cause']}</td>
                            <td>{error['line']}</td>
                            <td>{error['column']}</td>
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
    </body>
    </html>
    """
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_helm.py <path_to_helm_chart_directory>")
        sys.exit(1)

    root_dir = sys.argv[1]
    if not os.path.isdir(root_dir):
        print(f"ERROR: Directory not found at '{root_dir}'")
        sys.exit(1)
        
    validation_results = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if 'Chart.yaml' in filenames:
            result = validate_helm_chart(dirpath)
            validation_results.append(result)
            del dirnames[:]

    if not validation_results:
        print(f"No Helm charts found in directory '{root_dir}'")
        sys.exit(0)
    
    report_name = "helm_Validation_Report.html"
    generate_html_report(validation_results, report_name)
    print(f"\nValidation complete. Report generated at {report_name}")

if __name__ == "__main__":
    main()