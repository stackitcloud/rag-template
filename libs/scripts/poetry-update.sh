#!/bin/bash

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Function to display usage
usage() {
    cat << EOF
Pod Dependency Manager

This script manages Poetry dependencies in a Kubernetes pod.
It must be run from the local directory containing poetry.lock and pyproject.toml.

Usage: $(basename "$0") -n <namespace> -p <pod_name> [-s <source_folder>] <action> [dependency]

Options:
 -n <namespace>    Kubernetes namespace
 -p <pod_name>     Full or partial pod name
 -s <source_folder> Source folder in container (default: derived from current directory)

Actions:
 add <dependency>  Add a dependency
 remove <dependency> Remove a dependency
 lock              Update poetry.lock file

Examples:
 Assume you're in the /path/to/your/project directory containing poetry.lock and pyproject.toml:

 Add a dependency:
  $ cd /path/to/your/project
  $ ../scripts/$(basename "$0") -n myapp-namespace -p myapp-pod add requests

 Remove a dependency:
  $ cd /path/to/your/project
  $ ../scripts/$(basename "$0") -n myapp-namespace -p myapp-pod remove requests

 Update lock file:
  $ cd /path/to/your/project
  $ ../scripts/$(basename "$0") -n myapp-namespace -p myapp-pod lock

 Use a specific source folder:
  $ cd /path/to/your/project
  $ ../scripts/$(basename "$0") -n myapp-namespace -p myapp-pod -s /app/backend add pandas

 Real-world example (adding OpenAI package to RAG backend):
  $ cd /path/to/rag-backend
  $ ../rag-core-library/scripts/$(basename "$0") -n rag -p backend add openai
EOF
    exit 1
}

# Check if namespace and action are provided
if [ $# -lt 2 ]; then
    usage
fi


# Check if poetry.lock and pyproject.toml exist in the current directory
if [ ! -f "poetry.lock" ] || [ ! -f "pyproject.toml" ]; then
    echo "Error: poetry.lock and/or pyproject.toml not found in the current directory."
    echo "Please run this script from a directory containing both files."
    exit 1
fi

# Parse options
while getopts ":n:p:s:" opt; do
    case $opt in
        n) namespace="$OPTARG" ;;
        p) pod_name="$OPTARG" ;;
        s) source_folder="$OPTARG" ;;
        \?) echo "Invalid option -$OPTARG" >&2; usage ;;
    esac
done

# Shift to get action and dependency
shift $((OPTIND-1))
action=$1
dependency=$2

# Check if required options are provided
if [ -z "$namespace" ] || [ -z "$pod_name" ]; then
    echo "Error: Namespace (-n) and pod prefix (-p) are required"
    usage
fi

# Validate action
case $action in
    add|remove)
        if [ -z "$dependency" ]; then
            echo "Error: Dependency is required for add/remove actions"
            usage
        fi
        ;;
    lock)
        ;;
    *)
        echo "Error: Invalid action"
        usage
        ;;
esac


cd_cmd=""

# Determine source folder if not provided
if [ -z "$source_folder" ]; then
    current_dir=$(basename "$PWD")
    source_folder="/app/$current_dir"
else 
    cd_cmd="cd $source_folder &&"
fi

# Get all matching pod names
matching_pods=$(kubectl get pods -n "$namespace" --no-headers -o custom-columns=":metadata.name" | grep "^$pod_name")

# Count the number of matching pods
pod_count=$(echo "$matching_pods" | wc -l)

if [ $pod_count -eq 0 ]; then
    echo "No pod starting with $pod_name found in namespace $namespace"
    exit 1
elif [ $pod_count -gt 1 ]; then
    echo "Multiple pods found with the prefix $pod_name:"
    echo "$matching_pods"
    echo "Please provide a more specific name."
    exit 1
fi

# Get the exact pod name
pod_name=$(echo "$matching_pods" | head -n 1)

echo "Found pod: $pod_name"
echo "Using source folder: $source_folder"

# Perform the requested action
case $action in
    add)
        echo "Adding dependency: $dependency"
        kubectl exec --stdin --tty "$pod_name" -n "$namespace" -- bash -c "${cd_cmd} poetry add $dependency"
        ;;
    remove)
        echo "Removing dependency: $dependency"
        kubectl exec --stdin --tty "$pod_name" -n "$namespace" -- bash -c "${cd_cmd} poetry remove $dependency"
        ;;
    lock)
        echo "Updating poetry.lock file"
        kubectl exec --stdin --tty "$pod_name" -n "$namespace" -- bash -c "${cd_cmd} poetry lock"
        ;;
esac

# Copy files based on the action
echo "Copying poetry files to current directory"
kubectl cp "$namespace/$pod_name:$source_folder/poetry.lock" "./poetry.lock"
if [ "$action" != "lock" ]; then
    kubectl cp "$namespace/$pod_name:$source_folder/pyproject.toml" "./pyproject.toml"
fi

echo "Script completed successfully"
echo "Files saved in: $PWD"