import subprocess
import argparse
import difflib
import argparse
import os

def compare_dependency_files(file1_path, file2_path):
    """
    Compares two text files and generates a color-coded HTML report in the current working directory.
    """
    try:
        with open(file1_path, 'r', encoding='utf-8') as file1:
            file1_lines = file1.readlines()

        with open(file2_path, 'r', encoding='utf-8') as file2:
            file2_lines = file2.readlines()
    except FileNotFoundError as e:
        print(f"Error: One of the files was not found. {e}")
        return

    # Use difflib to create a HTML diff
    diff_generator = difflib.HtmlDiff()
    diff_report = diff_generator.make_file(file1_lines, file2_lines, fromdesc=file1_path, todesc=file2_path)

    # Get the current working directory and create the output file path
    current_dir = os.getcwd()
    output_report_path = os.path.join(current_dir, "project_dependency_diff_report.html")

    # Save the HTML report to a file
    with open(output_report_path, 'w', encoding='utf-8') as f:
        f.write(diff_report)

    print(f"Comparison complete. HTML report saved to '{output_report_path}'.")
    
def run_maven_dependency_tree(project_path1, project_path2, maven_path):
    """
    Executes 'mvn dependency:tree' using the specified Maven path and saves the output to a file.

    Args:
        project_path1 (str): The path to the first project root directory of the Maven project.
        project_path2 (str): The path to the second project root directory of the Maven project.
        maven_path (str): The absolute path to the 'mvn' executable.
    """
    # Create the output file path
    output_file_name1 = "dependencies1.txt"
    output_file_name2 = "dependencies2.txt"
    
    output_path1 = os.path.join(project_path1, output_file_name1)
    output_path2 = os.path.join(project_path2, output_file_name2)

    settings_path1 = os.path.join(project_path1, "settings.xml")
    settings_path2 = os.path.join(project_path2, "settings.xml")
    
    try:
        # ###############################################################
        # First Project - project_path1       
        # The command to execute, using the provided maven_path
        # command = [maven_path, "dependency:tree"]
        command1 = [maven_path, "dependency:tree", "--settings", settings_path1]
    
        # First Project - project_path1
        print(f"Running command: {' '.join(command1)} in directory '{project_path1}'...")
            
        # Run the command in the specified directory and capture its output
        result = subprocess.run(command1, cwd=project_path1, capture_output=True, text=True, check=True)

        # Save the captured standard output to the specified file
        # with open(output_path1, "w") as f:
        #     f.write(result.stdout)
        with open(output_path1, "w") as f:
            for line in result.stdout.splitlines():
                if line.strip().startswith("[INFO]"):
                    f.write(line + "\n")
                    
        print(f"Successfully generated dependency tree. Output saved to '{output_path1}'.")

        # ###############################################################
        # Second Project - project_path2
        command2 = [maven_path, "dependency:tree", "--settings", settings_path2]
        
        print(f"Running command: {' '.join(command2)} in directory '{project_path2}'...")
            
        # Run the command in the specified directory and capture its output
        result = subprocess.run(command2, cwd=project_path2, capture_output=True, text=True, check=True)

        # Save the captured standard output to the specified file
        # with open(output_path2, "w") as f:
        #     f.write(result.stdout)
        with open(output_path2, "w") as f:
            for line in result.stdout.splitlines():
                if line.strip().startswith("[INFO]"):
                    f.write(line + "\n")
                    
        print(f"Successfully generated dependency tree. Output saved to '{output_path2}'.")  

        compare_dependency_files(output_path1, output_path2)
    except FileNotFoundError:
        print(f"Error: The Maven executable was not found at '{maven_path}'. Please check the path.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running Maven in '{project_path1}' or '{project_path2}': {e}")
        print(f"Maven output:\n{e.stdout}")
        print(f"Maven error:\n{e.stderr}")

def check_project_path(path):
    """
    Checks if a given path is a valid directory containing a pom.xml file.
    Returns True if valid, False otherwise.
    """
    if not os.path.isdir(path):
        print(f"Error: The directory '{path}' does not exist.")
        return False
    elif not os.path.exists(os.path.join(path, "pom.xml")):
        print(f"Error: No pom.xml file found in '{path}'.")
        return False
    return True
    
# --- Main execution block ---
if __name__ == "__main__":
    # 1. Create the parser
    parser = argparse.ArgumentParser(description="Generate a Maven dependency tree for a project.")

    # 2. Add the positional arguments
    parser.add_argument(
        "project_path1",
        type=str,
        help="The first project path to the Maven project's root directory."
    )
    parser.add_argument(
        "project_path2",
        type=str,
        help="The second project path to the Maven project's root directory."
    )
    #parser.add_argument(
    #    "maven_path",
    #    type=str,
    #    help="The absolute path to the 'mvn' executable (e.g., C:\\apache-maven-3.8.1\\bin\\mvn.cmd)."
    #)

    # 3. Parse the command-line arguments
    args = parser.parse_args()

    # 4. Use the provided paths
    project_path1 = args.project_path1
    project_path2 = args.project_path2
    
    #maven_path = args.maven_path
    maven_path = "C:/DOCUMENTATION/MAVEN/apache-maven-3.9.10/bin/mvn.cmd"

    # 5. Validate the paths before running the command
    if check_project_path(project_path1) and check_project_path(project_path2):
        # Both paths are valid, proceed with the comparison
        run_maven_dependency_tree(project_path1, project_path2, maven_path)
    else:
        print("One or both project paths are invalid. Aborting.")