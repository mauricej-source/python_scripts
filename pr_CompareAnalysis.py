import subprocess
import os
import argparse
import difflib

# -------------------------------------------------------------
# Function Definitions
# -------------------------------------------------------------

def run_maven_dependency_tree(project_directory, maven_path):
    """
    Executes 'mvn dependency:tree' and filters the output.
    Returns the path to the generated dependencies.txt file.
    """
    output_file_name = "dependencies.txt"
    output_path = os.path.join(project_directory, output_file_name)
    settings_path = os.path.join(project_directory, "settings.xml")

    command = [maven_path, "dependency:tree", "--settings", settings_path]

    print(f"\nRunning command: {' '.join(command)} in directory '{project_directory}'...")

    try:
        result = subprocess.run(
            command,
            cwd=project_directory,
            capture_output=True,
            text=True,
            check=True
        )
        with open(output_path, "w") as f:
            for line in result.stdout.splitlines():
                if line.strip().startswith("[INFO]"):
                    f.write(line + "\n")
        print(f"Successfully generated filtered dependency tree. Output saved to '{output_path}'.")
        return output_path
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"An error occurred: {e}")
        return None

def analyze_tech_stack(dependencies_file):
    """
    Performs a comprehensive analysis of the technology stack, including version numbers,
    dependency counts, and potential conflicts.

    Args:
        dependencies_file (str): The path to the filtered dependencies.txt file.

    Returns:
        dict: A dictionary containing the detailed analysis results.
    """
    analysis = {
        "summary": {
            "total_dependencies": 0,
            "scopes": {"compile": 0, "test": 0, "runtime": 0, "provided": 0},
        },
        "core": {
            "web_framework": "Unknown",
            "server": "Unknown",
            "spring_boot_version": "Unknown",
        },
        "data_access": {"type": "Unknown", "database": "Unknown"},
        "messaging": {"type": "None"},
        "security": {"framework": "None"},
        "cloud": {"platform": "None"},
        "utility_libs": [],
        "testing_frameworks": [],
        "logging": {"framework": "Unknown"},
        "api_documentation": {"framework": "None"},
        "potential_conflicts": [],
    }

    try:
        with open(dependencies_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Dependency file not found at '{dependencies_file}'.")
        return analysis

    found_web_frameworks = []

    for line in lines:
        line = line.strip()

        # General Dependency Counting
        analysis["summary"]["total_dependencies"] += 1
        if "compile" in line:
            analysis["summary"]["scopes"]["compile"] += 1
        elif "test" in line:
            analysis["summary"]["scopes"]["test"] += 1
        elif "runtime" in line:
            analysis["summary"]["scopes"]["runtime"] += 1
        elif "provided" in line:
            analysis["summary"]["scopes"]["provided"] += 1

        # Core Stack and Version
        if "org.springframework.boot:spring-boot-starter:" in line:
            parts = line.split(":")
            if len(parts) >= 3:
                analysis["core"]["spring_boot_version"] = parts[2]

        if "spring-boot-starter-webflux" in line:
            analysis["core"]["web_framework"] = "Spring WebFlux (Reactive)"
            found_web_frameworks.append("WebFlux")
        elif "spring-boot-starter-web" in line:
            analysis["core"]["web_framework"] = "Spring MVC (Blocking)"
            found_web_frameworks.append("WebMVC")

        if "netty-all" in line or "reactor-netty" in line:
            if "Spring WebFlux" in analysis["core"]["web_framework"]:
                analysis["core"]["server"] = "Netty (Default for WebFlux)"
            else:
                analysis["core"]["server"] = "Netty (Non-Blocking)"
        elif "tomcat-embed-core" in line:
            if "Spring MVC" in analysis["core"]["web_framework"]:
                analysis["core"]["server"] = "Tomcat (Default for WebMVC)"
            else:
                analysis["core"]["server"] = "Tomcat (Blocking)"

        # Data Access
        if "spring-boot-starter-data-r2dbc" in line:
            analysis["data_access"]["type"] = "Reactive (R2DBC)"
        elif "spring-boot-starter-data-jpa" in line:
            analysis["data_access"]["type"] = "Blocking (JPA)"

        if "postgresql" in line:
            analysis["data_access"]["database"] = "PostgreSQL"
        elif "mongodb" in line:
            analysis["data_access"]["database"] = "MongoDB"
        elif "elasticsearch" in line:
            analysis["data_access"]["database"] = "Elasticsearch"

        # Messaging
        if "spring-kafka" in line:
            analysis["messaging"]["type"] = "Apache Kafka"
        elif "spring-rabbit" in line:
            analysis["messaging"]["type"] = "RabbitMQ"

        # Security
        if "spring-boot-starter-security" in line:
            analysis["security"]["framework"] = "Spring Security"
        elif "spring-security-oauth2-resource-server" in line:
            analysis["security"]["framework"] = "Spring Security OAuth2"

        # Cloud/AWS SDK
        if "software.amazon.awssdk" in line:
            analysis["cloud"]["platform"] = "AWS SDK"

        # Utility Libraries
        if "lombok" in line and "Lombok" not in analysis["utility_libs"]:
            analysis["utility_libs"].append("Lombok")
        if "guava" in line and "Google Guava" not in analysis["utility_libs"]:
            analysis["utility_libs"].append("Google Guava")
        if "jackson-databind" in line and "Jackson" not in analysis["utility_libs"]:
            analysis["utility_libs"].append("Jackson")

        # Testing Frameworks
        if "junit-jupiter" in line or "junit-vintage" in line:
            if "JUnit" not in analysis["testing_frameworks"]:
                analysis["testing_frameworks"].append("JUnit")
        if "mockito-core" in line and "Mockito" not in analysis["testing_frameworks"]:
            analysis["testing_frameworks"].append("Mockito")
        if "assertj-core" in line and "AssertJ" not in analysis["testing_frameworks"]:
            analysis["testing_frameworks"].append("AssertJ")

        # Logging Frameworks
        if "spring-boot-starter-logging" in line:
            analysis["logging"]["framework"] = "Spring Boot Starter Logging (Logback)"
        elif "log4j-core" in line:
            analysis["logging"]["framework"] = "Log4j"
        elif "slf4j-api" in line:
            if "Unknown" in analysis["logging"]["framework"]:
                analysis["logging"]["framework"] = "SLF4J"

        # API Documentation (OpenAPI/Swagger)
        if "springdoc-openapi" in line:
            analysis["api_documentation"]["framework"] = "SpringDoc OpenAPI"
        elif "swagger-ui" in line:
            analysis["api_documentation"]["framework"] = "Swagger UI"
        elif "springfox-swagger" in line:
            analysis["api_documentation"]["framework"] = "Springfox Swagger"

    # Final Conflict Check
    if len(set(found_web_frameworks)) > 1:
        analysis["potential_conflicts"].append(
            "Both Spring WebFlux and Spring MVC starters found."
        )

    return analysis
    
# def analyze_tech_stack(dependencies_file):
#     """
#     Performs a comprehensive analysis of the technology stack, including version numbers and potential conflicts.
#     
#     Args:
#         dependencies_file (str): The path to the filtered dependencies.txt file.
#         
#     Returns:
#         dict: A dictionary containing the detailed analysis results.
#     """
#     analysis = {
#         "core": {"web_framework": "Unknown", "server": "Unknown", "spring_boot_version": "Unknown"},
#         "data_access": {"type": "Unknown", "database": "Unknown"},
#         "messaging": {"type": "None"},
#         "security": {"framework": "None"},
#         "cloud": {"platform": "None"},
#         "potential_conflicts": []
#     }
#     
#     try:
#         with open(dependencies_file, 'r', encoding='utf-8') as f:
#             lines = f.readlines()
#     except FileNotFoundError:
#         print(f"Error: Dependency file not found at '{dependencies_file}'.")
#         return analysis
#         
#     found_web_frameworks = []
# 
#     for line in lines:
#         line = line.strip()
#         
#         # Core Stack and Version
#         if "org.springframework.boot:spring-boot-starter:" in line:
#             parts = line.split(":")
#             if len(parts) >= 3:
#                 analysis["core"]["spring_boot_version"] = parts[2]
#         
#         if "spring-boot-starter-webflux" in line:
#             analysis["core"]["web_framework"] = "Spring WebFlux (Reactive)"
#             found_web_frameworks.append("WebFlux")
#         elif "spring-boot-starter-web" in line:
#             analysis["core"]["web_framework"] = "Spring MVC (Blocking)"
#             found_web_frameworks.append("WebMVC")
#         
#         if "netty-all" in line or "reactor-netty" in line:
#             if "Spring WebFlux" in analysis["core"]["web_framework"]:
#                 analysis["core"]["server"] = "Netty (Default for WebFlux)"
#             else:
#                 analysis["core"]["server"] = "Netty (Non-Blocking)"
#         elif "tomcat-embed-core" in line:
#             if "Spring MVC" in analysis["core"]["web_framework"]:
#                 analysis["core"]["server"] = "Tomcat (Default for WebMVC)"
#             else:
#                 analysis["core"]["server"] = "Tomcat (Blocking)"
#             
#         # Data Access
#         if "spring-boot-starter-data-r2dbc" in line:
#             analysis["data_access"]["type"] = "Reactive (R2DBC)"
#         elif "spring-boot-starter-data-jpa" in line:
#             analysis["data_access"]["type"] = "Blocking (JPA)"
#         
#         if "postgresql" in line:
#             analysis["data_access"]["database"] = "PostgreSQL"
#         elif "mongodb" in line:
#             analysis["data_access"]["database"] = "MongoDB"
#         elif "elasticsearch" in line:
#             analysis["data_access"]["database"] = "Elasticsearch"
#             
#         # Messaging
#         if "spring-kafka" in line:
#             analysis["messaging"]["type"] = "Apache Kafka"
#         elif "spring-rabbit" in line:
#             analysis["messaging"]["type"] = "RabbitMQ"
# 
#         # Security
#         if "spring-boot-starter-security" in line:
#             analysis["security"]["framework"] = "Spring Security"
#         elif "spring-security-oauth2-resource-server" in line:
#             analysis["security"]["framework"] = "Spring Security OAuth2"
#             
#         # Cloud/AWS SDK
#         if "software.amazon.awssdk" in line:
#             analysis["cloud"]["platform"] = "AWS SDK"
#     
#     # Check for potential conflicts
#     if len(set(found_web_frameworks)) > 1:
#         analysis["potential_conflicts"].append("Both Spring WebFlux and Spring MVC starters found.")
# 
#     return analysis
    
# def analyze_tech_stack(dependencies_file):
#     """
#     Performs a comprehensive analysis of the technology stack.
#     """
#     analysis = {
#         "core": {"web_framework": "Unknown", "server": "Unknown"},
#         "data_access": {"type": "Unknown", "database": "Unknown"},
#         "messaging": {"type": "None"},
#         "security": {"framework": "None"},
#         "cloud": {"platform": "None"}
#     }
#     
#     try:
#         with open(dependencies_file, 'r', encoding='utf-8') as f:
#             lines = f.readlines()
#     except FileNotFoundError:
#         print(f"Error: Dependency file not found at '{dependencies_file}'.")
#         return analysis
#         
#     for line in lines:
#         if "spring-boot-starter-webflux" in line:
#             analysis["core"]["web_framework"] = "Spring WebFlux (Reactive)"
#         elif "spring-boot-starter-web" in line:
#             analysis["core"]["web_framework"] = "Spring MVC (Blocking)"
#         elif "netty-all" in line or "reactor-netty" in line:
#             analysis["core"]["server"] = "Netty (Non-Blocking)"
#         elif "tomcat-embed-core" in line:
#             analysis["core"]["server"] = "Tomcat (Blocking)"
#         elif "spring-boot-starter-data-r2dbc" in line:
#             analysis["data_access"]["type"] = "Reactive (R2DBC)"
#         elif "spring-boot-starter-data-jpa" in line:
#             analysis["data_access"]["type"] = "Blocking (JPA)"
#         elif "postgresql" in line:
#             analysis["data_access"]["database"] = "PostgreSQL"
#         elif "mongodb" in line:
#             analysis["data_access"]["database"] = "MongoDB"
#         elif "elasticsearch" in line:
#             analysis["data_access"]["database"] = "Elasticsearch"
#         elif "spring-kafka" in line:
#             analysis["messaging"]["type"] = "Apache Kafka"
#         elif "spring-rabbit" in line:
#             analysis["messaging"]["type"] = "RabbitMQ"
#         elif "spring-boot-starter-security" in line:
#             analysis["security"]["framework"] = "Spring Security"
#         elif "spring-security-oauth2-resource-server" in line:
#             analysis["security"]["framework"] = "Spring Security OAuth2"
#         elif "software.amazon.awssdk" in line:
#             analysis["cloud"]["platform"] = "AWS SDK"
# 
#     return analysis

def create_html_report(project1_analysis, project2_analysis, file1_path, file2_path):
    """
    Generates a single HTML report comparing the two projects' analysis results.
    """
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Project Comparison Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            .container {{ display: flex; justify-content: space-between; gap: 20px; }}
            .project {{ flex: 1; padding: 20px; border: 1px solid #ccc; border-radius: 8px; }}
            h2 {{ border-bottom: 2px solid #333; padding-bottom: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f2f2f2; }}
            .diff {{ color: #d9534f; font-weight: bold; }}
            .conflict {{ color: red; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>Project Comparison Report</h1>
        <div class="container">
            <div class="project">
                <h2>Project 1:<br><span style="font-size: 0.5em;">{0}</span></h2>
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Analysis</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>Spring Boot Version</td><td>{1}</td></tr>
                        <tr><td>Web Framework</td><td>{2}</td></tr>
                        <tr><td>Server</td><td>{3}</td></tr>
                        <tr><td>Data Access</td><td>{4}</td></tr>
                        <tr><td>Database</td><td>{5}</td></tr>
                        <tr><td>Messaging</td><td>{6}</td></tr>
                        <tr><td>Security</td><td>{7}</td></tr>
                        <tr><td>Cloud</td><td>{8}</td></tr>
                        <tr><td>Logging Framework</td><td>{9}</td></tr>
                        <tr><td>API Documentation</td><td>{10}</td></tr>
                        <tr><td>Conflicts</td><td>{11}</td></tr>
                    </tbody>
                </table>
            </div>
            <div class="project">
                <h2>Project 2:<br><span style="font-size: 0.5em;">{12}</span></h2>
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Analysis</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>Spring Boot Version</td><td>{13}</td></tr>
                        <tr><td>Web Framework</td><td>{14}</td></tr>
                        <tr><td>Server</td><td>{15}</td></tr>
                        <tr><td>Data Access</td><td>{16}</td></tr>
                        <tr><td>Database</td><td>{17}</td></tr>
                        <tr><td>Messaging</td><td>{18}</td></tr>
                        <tr><td>Security</td><td>{19}</td></tr>
                        <tr><td>Cloud</td><td>{20}</td></tr>
                        <tr><td>Logging Framework</td><td>{21}</td></tr>
                        <tr><td>API Documentation</td><td>{22}</td></tr>
                        <tr><td>Conflicts</td><td>{23}</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
        <hr>
        <h2>Detailed Dependency Diff</h2>
    """.format(
        os.path.abspath(os.path.dirname(file1_path)),
        project1_analysis["core"]["spring_boot_version"],
        project1_analysis["core"]["web_framework"],
        project1_analysis["core"]["server"],
        project1_analysis["data_access"]["type"],
        project1_analysis["data_access"]["database"],
        project1_analysis["messaging"]["type"],
        project1_analysis["security"]["framework"],
        project1_analysis["cloud"]["platform"],
        project1_analysis["logging"]["framework"],
        project1_analysis["api_documentation"]["framework"],
        ", ".join(project1_analysis["potential_conflicts"]) if project1_analysis["potential_conflicts"] else "None",
        os.path.abspath(os.path.dirname(file2_path)),
        project2_analysis["core"]["spring_boot_version"],
        project2_analysis["core"]["web_framework"],
        project2_analysis["core"]["server"],
        project2_analysis["data_access"]["type"],
        project2_analysis["data_access"]["database"],
        project2_analysis["messaging"]["type"],
        project2_analysis["security"]["framework"],
        project2_analysis["cloud"]["platform"],
        project2_analysis["logging"]["framework"],
        project2_analysis["api_documentation"]["framework"],
        ", ".join(project2_analysis["potential_conflicts"]) if project2_analysis["potential_conflicts"] else "None"
    )
    
    with open(file1_path, 'r', encoding='utf-8') as f1, open(file2_path, 'r', encoding='utf-8') as f2:
        diff_generator = difflib.HtmlDiff()
        diff_html = diff_generator.make_file(f1.readlines(), f2.readlines(), fromdesc=os.path.abspath(os.path.dirname(file1_path)), todesc=os.path.abspath(os.path.dirname(file2_path)))
    
    html_template += diff_html
    html_template += """
    </body>
    </html>
    """
    
    output_path = "projectComp_Report.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_template)
        
    return output_path
    
# def create_html_report(project1_analysis, project2_analysis, file1_path, file2_path):
#     """
#     Generates a single HTML report comparing the two projects' analysis results.
#     """
#     html_template = """
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#         <meta charset="UTF-8">
#         <title>Project Comparison Report</title>
#         <style>
#             body {{ font-family: Arial, sans-serif; margin: 20px; }}
#             h1 {{ color: #333; }}
#             .container {{ display: flex; justify-content: space-between; gap: 20px; }}
#             .project {{ flex: 1; padding: 20px; border: 1px solid #ccc; border-radius: 8px; }}
#             h2 {{ border-bottom: 2px solid #333; padding-bottom: 5px; }}
#             table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
#             th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
#             th {{ background-color: #f2f2f2; }}
#             .diff {{ color: #d9534f; font-weight: bold; }}
#         </style>
#     </head>
#     <body>
#         <h1>Project Comparison Report</h1>
#         <div class="container">
#             <div class="project">
#                 <h2>Project 1:<br><span style="font-size: 0.5em;">{0}</span></h2>
#                 <table>
#                     <thead>
#                         <tr>
#                             <th>Category</th>
#                             <th>Analysis</th>
#                         </tr>
#                     </thead>
#                     <tbody>
#                         <tr><td>Web Framework</td><td>{1}</td></tr>
#                         <tr><td>Server</td><td>{2}</td></tr>
#                         <tr><td>Data Access</td><td>{3}</td></tr>
#                         <tr><td>Database</td><td>{4}</td></tr>
#                         <tr><td>Messaging</td><td>{5}</td></tr>
#                         <tr><td>Security</td><td>{6}</td></tr>
#                         <tr><td>Cloud</td><td>{7}</td></tr>
#                     </tbody>
#                 </table>
#             </div>
#             <div class="project">
#                 <h2>Project 2:<br><span style="font-size: 0.5em;">{8}</span></h2>
#                 <table>
#                     <thead>
#                         <tr>
#                             <th>Category</th>
#                             <th>Analysis</th>
#                         </tr>
#                     </thead>
#                     <tbody>
#                         <tr><td>Web Framework</td><td>{9}</td></tr>
#                         <tr><td>Server</td><td>{10}</td></tr>
#                         <tr><td>Data Access</td><td>{11}</td></tr>
#                         <tr><td>Database</td><td>{12}</td></tr>
#                         <tr><td>Messaging</td><td>{13}</td></tr>
#                         <tr><td>Security</td><td>{14}</td></tr>
#                         <tr><td>Cloud</td><td>{15}</td></tr>
#                     </tbody>
#                 </table>
#             </div>
#         </div>
#         <hr>
#         <h2>Detailed Dependency Diff</h2>
#     """.format(
#         os.path.abspath(os.path.dirname(file1_path)),
#         project1_analysis["core"]["web_framework"],
#         project1_analysis["core"]["server"],
#         project1_analysis["data_access"]["type"],
#         project1_analysis["data_access"]["database"],
#         project1_analysis["messaging"]["type"],
#         project1_analysis["security"]["framework"],
#         project1_analysis["cloud"]["platform"],
#         os.path.abspath(os.path.dirname(file2_path)),
#         project2_analysis["core"]["web_framework"],
#         project2_analysis["core"]["server"],
#         project2_analysis["data_access"]["type"],
#         project2_analysis["data_access"]["database"],
#         project2_analysis["messaging"]["type"],
#         project2_analysis["security"]["framework"],
#         project2_analysis["cloud"]["platform"]
#     )
#     
#     with open(file1_path, 'r', encoding='utf-8') as f1, open(file2_path, 'r', encoding='utf-8') as f2:
#         diff_generator = difflib.HtmlDiff()
#         # Also use full paths in the diff report description
#         diff_html = diff_generator.make_file(f1.readlines(), f2.readlines(), fromdesc=file1_path, todesc=file2_path)
#     
#     html_template += diff_html
#     html_template += """
#     </body>
#     </html>
#     """
#     
#     output_path = "projectComp_Report.html"
#     with open(output_path, "w", encoding="utf-8") as f:
#         f.write(html_template)
#         
#     return output_path
    
# def create_html_report(project1_analysis, project2_analysis, file1_path, file2_path):
#     """
#     Generates a single HTML report comparing the two projects' analysis results.
#     """
#     html_template = """
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#         <meta charset="UTF-8">
#         <title>Project Comparison Report</title>
#         <style>
#             body {{ font-family: Arial, sans-serif; margin: 20px; }}
#             h1 {{ color: #333; }}
#             .container {{ display: flex; justify-content: space-between; gap: 20px; }}
#             .project {{ flex: 1; padding: 20px; border: 1px solid #ccc; border-radius: 8px; }}
#             h2 {{ border-bottom: 2px solid #333; padding-bottom: 5px; }}
#             table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
#             th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
#             th {{ background-color: #f2f2f2; }}
#             .diff {{ color: #d9534f; font-weight: bold; }}
#         </style>
#     </head>
#     <body>
#         <h1>Project Comparison Report</h1>
#         <div class="container">
#             <div class="project">
#                 <h2>Project 1:<br><span style="font-size: 0.5em;">{0}</span></h2>
#                 <table>
#                     <thead>
#                         <tr>
#                             <th>Category</th>
#                             <th>Analysis</th>
#                         </tr>
#                     </thead>
#                     <tbody>
#                         <tr><td>Web Framework</td><td>{1}</td></tr>
#                         <tr><td>Server</td><td>{2}</td></tr>
#                         <tr><td>Data Access</td><td>{3}</td></tr>
#                         <tr><td>Database</td><td>{4}</td></tr>
#                         <tr><td>Messaging</td><td>{5}</td></tr>
#                         <tr><td>Security</td><td>{6}</td></tr>
#                         <tr><td>Cloud</td><td>{7}</td></tr>
#                     </tbody>
#                 </table>
#             </div>
#             <div class="project">
#                 <h2>Project 2:<br><span style="font-size: 0.5em;">{8}</span></h2>
#                 <table>
#                     <thead>
#                         <tr>
#                             <th>Category</th>
#                             <th>Analysis</th>
#                         </tr>
#                     </thead>
#                     <tbody>
#                         <tr><td>Web Framework</td><td>{9}</td></tr>
#                         <tr><td>Server</td><td>{10}</td></tr>
#                         <tr><td>Data Access</td><td>{11}</td></tr>
#                         <tr><td>Database</td><td>{12}</td></tr>
#                         <tr><td>Messaging</td><td>{13}</td></tr>
#                         <tr><td>Security</td><td>{14}</td></tr>
#                         <tr><td>Cloud</td><td>{15}</td></tr>
#                     </tbody>
#                 </table>
#             </div>
#         </div>
#         <hr>
#         <h2>Detailed Dependency Diff</h2>
#     """.format(
#         os.path.abspath(os.path.dirname(file1_path)),
#         project1_analysis["core"]["web_framework"],
#         project1_analysis["core"]["server"],
#         project1_analysis["data_access"]["type"],
#         project1_analysis["data_access"]["database"],
#         project1_analysis["messaging"]["type"],
#         project1_analysis["security"]["framework"],
#         project1_analysis["cloud"]["platform"],
#         os.path.abspath(os.path.dirname(file2_path)),
#         project2_analysis["core"]["web_framework"],
#         project2_analysis["core"]["server"],
#         project2_analysis["data_access"]["type"],
#         project2_analysis["data_access"]["database"],
#         project2_analysis["messaging"]["type"],
#         project2_analysis["security"]["framework"],
#         project2_analysis["cloud"]["platform"]
#     )
#     
#     with open(file1_path, 'r', encoding='utf-8') as f1, open(file2_path, 'r', encoding='utf-8') as f2:
#         diff_generator = difflib.HtmlDiff()
#         # Also use full paths in the diff report description
#         diff_html = diff_generator.make_file(f1.readlines(), f2.readlines(), fromdesc=file1_path, todesc=file2_path)
#     
#     html_template += diff_html
#     html_template += """
#     </body>
#     </html>
#     """
#     
#     output_path = "projectComp_Report.html"
#     with open(output_path, "w", encoding="utf-8") as f:
#         f.write(html_template)
#         
#     return output_path
    
# def create_html_report(project1_analysis, project2_analysis, file1_path, file2_path):
#     """
#     Generates a single HTML report comparing the two projects' analysis results.
#     """
#     html_template = """
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#         <meta charset="UTF-8">
#         <title>Project Comparison Report</title>
#         <style>
#             body {{ font-family: Arial, sans-serif; margin: 20px; }}
#             h1 {{ color: #333; }}
#             .container {{ display: flex; justify-content: space-between; gap: 20px; }}
#             .project {{ flex: 1; padding: 20px; border: 1px solid #ccc; border-radius: 8px; }}
#             h2 {{ border-bottom: 2px solid #333; padding-bottom: 5px; }}
#             table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
#             th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
#             th {{ background-color: #f2f2f2; }}
#             .diff {{ color: #d9534f; font-weight: bold; }}
#         </style>
#     </head>
#     <body>
#         <h1>Project Comparison Report</h1>
#         <div class="container">
#             <div class="project">
#                 <h2>Project 1: {0}</h2>
#                 <table>
#                     <thead>
#                         <tr>
#                             <th>Category</th>
#                             <th>Analysis</th>
#                         </tr>
#                     </thead>
#                     <tbody>
#                         <tr><td>Web Framework</td><td>{1}</td></tr>
#                         <tr><td>Server</td><td>{2}</td></tr>
#                         <tr><td>Data Access</td><td>{3}</td></tr>
#                         <tr><td>Database</td><td>{4}</td></tr>
#                         <tr><td>Messaging</td><td>{5}</td></tr>
#                         <tr><td>Security</td><td>{6}</td></tr>
#                         <tr><td>Cloud</td><td>{7}</td></tr>
#                     </tbody>
#                 </table>
#             </div>
#             <div class="project">
#                 <h2>Project 2: {8}</h2>
#                 <table>
#                     <thead>
#                         <tr>
#                             <th>Category</th>
#                             <th>Analysis</th>
#                         </tr>
#                     </thead>
#                     <tbody>
#                         <tr><td>Web Framework</td><td>{9}</td></tr>
#                         <tr><td>Server</td><td>{10}</td></tr>
#                         <tr><td>Data Access</td><td>{11}</td></tr>
#                         <tr><td>Database</td><td>{12}</td></tr>
#                         <tr><td>Messaging</td><td>{13}</td></tr>
#                         <tr><td>Security</td><td>{14}</td></tr>
#                         <tr><td>Cloud</td><td>{15}</td></tr>
#                     </tbody>
#                 </table>
#             </div>
#         </div>
#         <hr>
#         <h2>Detailed Dependency Diff</h2>
#     """.format(
#         # Use the full file paths for the titles
#         file1_path,
#         project1_analysis["core"]["web_framework"],
#         project1_analysis["core"]["server"],
#         project1_analysis["data_access"]["type"],
#         project1_analysis["data_access"]["database"],
#         project1_analysis["messaging"]["type"],
#         project1_analysis["security"]["framework"],
#         project1_analysis["cloud"]["platform"],
#         file2_path,
#         project2_analysis["core"]["web_framework"],
#         project2_analysis["core"]["server"],
#         project2_analysis["data_access"]["type"],
#         project2_analysis["data_access"]["database"],
#         project2_analysis["messaging"]["type"],
#         project2_analysis["security"]["framework"],
#         project2_analysis["cloud"]["platform"]
#     )
#     
#     with open(file1_path, 'r', encoding='utf-8') as f1, open(file2_path, 'r', encoding='utf-8') as f2:
#         diff_generator = difflib.HtmlDiff()
#         # Also use full paths in the diff report description
#         diff_html = diff_generator.make_file(f1.readlines(), f2.readlines(), fromdesc=file1_path, todesc=file2_path)
#     
#     html_template += diff_html
#     html_template += """
#     </body>
#     </html>
#     """
#     
#     output_path = "comparison_report.html"
#     with open(output_path, "w", encoding="utf-8") as f:
#         f.write(html_template)
#         
#     return output_path
    
# def create_html_report(project1_analysis, project2_analysis, file1_path, file2_path):
#     """
#     Generates a single HTML report comparing the two projects' analysis results.
#     """
#     html_template = """
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#         <meta charset="UTF-8">
#         <title>Project Comparison Report</title>
#         <style>
#             body {{ font-family: Arial, sans-serif; margin: 20px; }}
#             h1 {{ color: #333; }}
#             .container {{ display: flex; justify-content: space-between; gap: 20px; }}
#             .project {{ flex: 1; padding: 20px; border: 1px solid #ccc; border-radius: 8px; }}
#             h2 {{ border-bottom: 2px solid #333; padding-bottom: 5px; }}
#             table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
#             th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }}
#             th {{ background-color: #f2f2f2; }}
#             .diff {{ color: #d9534f; font-weight: bold; }}
#         </style>
#     </head>
#     <body>
#         <h1>Project Comparison Report</h1>
#         <div class="container">
#             <div class="project">
#                 <h2>Project 1: {0}</h2>
#                 <table>
#                     <thead>
#                         <tr>
#                             <th>Category</th>
#                             <th>Analysis</th>
#                         </tr>
#                     </thead>
#                     <tbody>
#                         <tr><td>Web Framework</td><td>{1}</td></tr>
#                         <tr><td>Server</td><td>{2}</td></tr>
#                         <tr><td>Data Access</td><td>{3}</td></tr>
#                         <tr><td>Database</td><td>{4}</td></tr>
#                         <tr><td>Messaging</td><td>{5}</td></tr>
#                         <tr><td>Security</td><td>{6}</td></tr>
#                         <tr><td>Cloud</td><td>{7}</td></tr>
#                     </tbody>
#                 </table>
#             </div>
#             <div class="project">
#                 <h2>Project 2: {8}</h2>
#                 <table>
#                     <thead>
#                         <tr>
#                             <th>Category</th>
#                             <th>Analysis</th>
#                         </tr>
#                     </thead>
#                     <tbody>
#                         <tr><td>Web Framework</td><td>{9}</td></tr>
#                         <tr><td>Server</td><td>{10}</td></tr>
#                         <tr><td>Data Access</td><td>{11}</td></tr>
#                         <tr><td>Database</td><td>{12}</td></tr>
#                         <tr><td>Messaging</td><td>{13}</td></tr>
#                         <tr><td>Security</td><td>{14}</td></tr>
#                         <tr><td>Cloud</td><td>{15}</td></tr>
#                     </tbody>
#                 </table>
#             </div>
#         </div>
#         <hr>
#         <h2>Detailed Dependency Diff</h2>
#     """.format(
#         os.path.basename(file1_path),
#         project1_analysis["core"]["web_framework"],
#         project1_analysis["core"]["server"],
#         project1_analysis["data_access"]["type"],
#         project1_analysis["data_access"]["database"],
#         project1_analysis["messaging"]["type"],
#         project1_analysis["security"]["framework"],
#         project1_analysis["cloud"]["platform"],
#         os.path.basename(file2_path),
#         project2_analysis["core"]["web_framework"],
#         project2_analysis["core"]["server"],
#         project2_analysis["data_access"]["type"],
#         project2_analysis["data_access"]["database"],
#         project2_analysis["messaging"]["type"],
#         project2_analysis["security"]["framework"],
#         project2_analysis["cloud"]["platform"]
#     )
#     
#     with open(file1_path, 'r', encoding='utf-8') as f1, open(file2_path, 'r', encoding='utf-8') as f2:
#         diff_generator = difflib.HtmlDiff()
#         diff_html = diff_generator.make_file(f1.readlines(), f2.readlines(), fromdesc=os.path.basename(file1_path), todesc=os.path.basename(file2_path))
#     
#     html_template += diff_html
#     html_template += """
#     </body>
#     </html>
#     """
#     
#     output_path = "comparison_report.html"
#     with open(output_path, "w", encoding="utf-8") as f:
#         f.write(html_template)
#         
#     return output_path
    
# def create_html_report(project1_analysis, project2_analysis, file1_path, file2_path):
#     """
#     Generates a single HTML report comparing the two projects' analysis results.
#     """
#     html_template = """
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#         <meta charset="UTF-8">
#         <title>Project Comparison Report</title>
#         <style>
#             body { font-family: Arial, sans-serif; margin: 20px; }
#             h1 { color: #333; }
#             .container { display: flex; justify-content: space-between; gap: 20px; }
#             .project { flex: 1; padding: 20px; border: 1px solid #ccc; border-radius: 8px; }
#             h2 { border-bottom: 2px solid #333; padding-bottom: 5px; }
#             table { width: 100%; border-collapse: collapse; margin-top: 15px; }
#             th, td { text-align: left; padding: 8px; border-bottom: 1px solid #ddd; }
#             th { background-color: #f2f2f2; }
#             .diff { color: #d9534f; font-weight: bold; }
#         </style>
#     </head>
#     <body>
#         <h1>Project Comparison Report</h1>
#         <div class="container">
#             <div class="project">
#                 <h2>Project 1: {0}</h2>
#                 <table>
#                     <thead>
#                         <tr>
#                             <th>Category</th>
#                             <th>Analysis</th>
#                         </tr>
#                     </thead>
#                     <tbody>
#                         <tr><td>Web Framework</td><td>{1}</td></tr>
#                         <tr><td>Server</td><td>{2}</td></tr>
#                         <tr><td>Data Access</td><td>{3}</td></tr>
#                         <tr><td>Database</td><td>{4}</td></tr>
#                         <tr><td>Messaging</td><td>{5}</td></tr>
#                         <tr><td>Security</td><td>{6}</td></tr>
#                         <tr><td>Cloud</td><td>{7}</td></tr>
#                     </tbody>
#                 </table>
#             </div>
#             <div class="project">
#                 <h2>Project 2: {8}</h2>
#                 <table>
#                     <thead>
#                         <tr>
#                             <th>Category</th>
#                             <th>Analysis</th>
#                         </tr>
#                     </thead>
#                     <tbody>
#                         <tr><td>Web Framework</td><td>{9}</td></tr>
#                         <tr><td>Server</td><td>{10}</td></tr>
#                         <tr><td>Data Access</td><td>{11}</td></tr>
#                         <tr><td>Database</td><td>{12}</td></tr>
#                         <tr><td>Messaging</td><td>{13}</td></tr>
#                         <tr><td>Security</td><td>{14}</td></tr>
#                         <tr><td>Cloud</td><td>{15}</td></tr>
#                     </tbody>
#                 </table>
#             </div>
#         </div>
#         <hr>
#         <h2>Detailed Dependency Diff</h2>
#     """.format(
#         os.path.basename(file1_path),
#         project1_analysis["core"]["web_framework"],
#         project1_analysis["core"]["server"],
#         project1_analysis["data_access"]["type"],
#         project1_analysis["data_access"]["database"],
#         project1_analysis["messaging"]["type"],
#         project1_analysis["security"]["framework"],
#         project1_analysis["cloud"]["platform"],
#         os.path.basename(file2_path),
#         project2_analysis["core"]["web_framework"],
#         project2_analysis["core"]["server"],
#         project2_analysis["data_access"]["type"],
#         project2_analysis["data_access"]["database"],
#         project2_analysis["messaging"]["type"],
#         project2_analysis["security"]["framework"],
#         project2_analysis["cloud"]["platform"]
#     )
#     
#     with open(file1_path, 'r', encoding='utf-8') as f1, open(file2_path, 'r', encoding='utf-8') as f2:
#         diff_generator = difflib.HtmlDiff()
#         diff_html = diff_generator.make_file(f1.readlines(), f2.readlines(), fromdesc=os.path.basename(file1_path), todesc=os.path.basename(file2_path))
#     
#     html_content += diff_html
#     html_content += """
#     </body>
#     </html>
#     """
#     
#     output_path = "comparison_report.html"
#     with open(output_path, "w", encoding="utf-8") as f:
#         f.write(html_content)
#         
#     return output_path

def check_project_path(path):
    """
    Checks if a given path is a valid directory containing a pom.xml file.
    """
    if not os.path.isdir(path):
        print(f"Error: The directory '{path}' does not exist.")
        return False
    if not os.path.exists(os.path.join(path, "pom.xml")):
        print(f"Error: No pom.xml file found in '{path}'.")
        return False
    if not os.path.exists(os.path.join(path, "settings.xml")):
        print(f"Error: No settings.xml file found in '{path}'.")
        return False
    return True

# -------------------------------------------------------------
# Main Execution Block
# -------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Compare two Maven projects.")
    parser.add_argument("project1_path", help="Path to the first Maven project's root directory.")
    parser.add_argument("project2_path", help="Path to the second Maven project's root directory.")
    #parser.add_argument("maven_path", help="The absolute path to the 'mvn' executable.")
    args = parser.parse_args()

    project1_path = args.project1_path
    project2_path = args.project2_path
    #maven_path = args.maven_path
    maven_path = "C:/DOCUMENTATION/MAVEN/apache-maven-3.9.10/bin/mvn.cmd"

    if not check_project_path(project1_path) or not check_project_path(project2_path):
        print("One or both project paths are invalid. Aborting.")
        return

    # Step 1: Run Maven on both projects and get the output file paths
    project1_deps_file = run_maven_dependency_tree(project1_path, maven_path)
    if not project1_deps_file:
        return
    
    project2_deps_file = run_maven_dependency_tree(project2_path, maven_path)
    if not project2_deps_file:
        return

    # Step 2: Analyze the dependency files
    project1_analysis = analyze_tech_stack(project1_deps_file)
    project2_analysis = analyze_tech_stack(project2_deps_file)
    
    # Step 3: Create and save the final HTML report
    report_path = create_html_report(project1_analysis, project2_analysis, project1_deps_file, project2_deps_file)
    print(f"\nFinal comparison report generated at: {os.path.abspath(report_path)}")

if __name__ == "__main__":
    main()