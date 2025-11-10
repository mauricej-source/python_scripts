import subprocess
import os
import argparse

def run_maven_dependency_tree(project_directory, maven_path):
    """
    Executes 'mvn dependency:tree' using the specified Maven path and saves the output to a file.

    Args:
        project_directory (str): The path to the root directory of the Maven project.
        maven_path (str): The absolute path to the 'mvn' executable.
    """
    # Create the output file path
    output_file_name = "dependencies.txt"
    output_path = os.path.join(project_directory, output_file_name)

    # The command to execute, using the provided maven_path
    command = [maven_path, "dependency:tree"]

    print(f"Running command: {' '.join(command)} in directory '{project_directory}'...")

    try:
        # Run the command in the specified directory and capture its output
        result = subprocess.run(command, cwd=project_directory, capture_output=True, text=True, check=True)

        # Save the captured standard output to the specified file
        with open(output_path, "w") as f:
            f.write(result.stdout)

        print(f"Successfully generated dependency tree. Output saved to '{output_path}'.")

    except FileNotFoundError:
        print(f"Error: The Maven executable was not found at '{maven_path}'. Please check the path.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running Maven in '{project_directory}': {e}")
        print(f"Maven output:\n{e.stdout}")
        print(f"Maven error:\n{e.stderr}")

# --- Main execution block ---
if __name__ == "__main__":
    # 1. Create the parser
    parser = argparse.ArgumentParser(description="Generate a Maven dependency tree for a project.")

    # 2. Add the positional arguments
    parser.add_argument(
        "project_path",
        type=str,
        help="The path to the Maven project's root directory."
    )
    #parser.add_argument(
    #    "maven_path",
    #    type=str,
    #    help="The absolute path to the 'mvn' executable (e.g., C:\\apache-maven-3.8.1\\bin\\mvn.cmd)."
    #)

    # 3. Parse the command-line arguments
    args = parser.parse_args()

    # 4. Use the provided paths
    project_path = args.project_path
    #maven_path = args.maven_path
    maven_path = "C:/DOCUMENTATION/MAVEN/apache-maven-3.9.10/bin/mvn.cmd"

    # 5. Validate the paths before running the command
    if not os.path.isdir(project_path):
        print(f"Error: The directory '{project_path}' does not exist.")
    elif not os.path.exists(os.path.join(project_path, "pom.xml")):
        print(f"Error: No pom.xml file found at '{project_path}'.")
    else:
        run_maven_dependency_tree(project_path, maven_path)