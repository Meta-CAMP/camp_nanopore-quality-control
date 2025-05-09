#!/bin/bash

# This script sets up the environment for CAMP Nanopore Long-Read Quality Control by configuring databases and Conda environments.
# It performs the following tasks:
# 1. Displays a welcome message.
# 2. Asks the user if each required database is already installed or needs to be installed.
# 3. Installs the databases if needed.
# 4. Sets up the working directory.
# 5. Checks if the required Conda environments are already installed and installs them if necessary.
# 6. Generates configuration files for parameters and test data input CSV.

# Functions:
# - show_welcome: Displays a welcome message with ASCII art and setup information.
# - ask_database: Prompts the user to provide the path to an existing database or installs the database if not available.
# - install_database: Downloads and installs the specified database in the given directory.
# - check_conda_env: Checks if a specific Conda environment is already installed.

# Variables:
# - MODULE_WORK_DIR: The working directory of the module.
# - USER_WORK_DIR: The user-specified working directory.
# - SETUP_WORK_DIR: The resolved working directory.
# - DB_SUBDIRS: An associative array mapping database variable names to their subdirectory paths.
# - DATABASE_PATHS: An associative array storing the paths to the databases.
# - DEFAULT_CONDA_ENV_DIR: The default directory for Conda environments.
# - PARAMS_FILE: The path to the parameters configuration file.
# - INPUT_CSV: The path to the test data input CSV file.

# The script concludes by generating the necessary configuration files and test data input CSV, and provides instructions for testing the workflow.

# --- Functions ---

show_welcome() {
    clear  # Clear the screen for a clean look

    echo ""
    sleep 0.2
    echo " _   _      _ _          ____    _    __  __ ____           _ "
    sleep 0.2
    echo "| | | | ___| | | ___    / ___|  / \  |  \/  |  _ \ ___ _ __| |"
    sleep 0.2
    echo "| |_| |/ _ \ | |/ _ \  | |     / _ \ | |\/| | |_) / _ \ '__| |"
    sleep 0.2
    echo "|  _  |  __/ | | (_) | | |___ / ___ \| |  | |  __/  __/ |  |_|"
    sleep 0.2
    echo "|_| |_|\___|_|_|\___/   \____/_/   \_\_|  |_|_|   \___|_|  (_)"
    sleep 0.5

    echo ""
    echo "🌲🏕️  WELCOME TO CAMP SETUP! 🏕️🌲"
    echo "===================================================="
    echo ""
    echo "   🏕️  Configuring Databases & Conda Environments"
    echo "       for CAMP Nanopore Long-Read Quality Control"
    echo ""
    echo "   🔥 Let's get everything set up properly!"
    echo ""
    echo "===================================================="
    echo ""

}

# Check to see if the base CAMP environment has already been installed 
find_install_camp_env() {
    if conda env list | grep -q "$DEFAULT_CONDA_ENV_DIR/camp"; then 
        echo "✅ The main CAMP environment is already installed in $DEFAULT_CONDA_ENV_DIR."
    else
        echo "🚀 Installing the main CAMP environment in $DEFAULT_CONDA_ENV_DIR/..."
        conda create --prefix "$DEFAULT_CONDA_ENV_DIR/camp" -c conda-forge -c bioconda biopython blast bowtie2 bumpversion click click-default-group cookiecutter jupyter matplotlib numpy pandas samtools scikit-learn scipy seaborn snakemake umap-learn upsetplot
        echo "✅ The main CAMP environment has been installed successfully!"
    fi
}

# Check to see if the required conda environments have already been installed 
find_install_conda_env() {
    if conda env list | grep -q "$DEFAULT_CONDA_ENV_DIR/$1"; then
        echo "✅ The $1 environment is already installed in $DEFAULT_CONDA_ENV_DIR."
    else
        echo "🚀 Installing $1 in $DEFAULT_CONDA_ENV_DIR/$1..."
        conda create --prefix $DEFAULT_CONDA_ENV_DIR/$1 -c conda-forge -c bioconda $1
        echo "✅ $1 installed successfully!"
    fi
}

# Ask user if each database is already installed or needs to be installed
ask_database() {
    local DB_NAME="$1"
    local DB_VAR_NAME="$2"
    local DB_PATH=""

    echo "🛠️  Checking for $DB_NAME database..."

    while true; do
        read -p "❓ Do you already have $DB_NAME installed? (y/n): " RESPONSE
        case "$RESPONSE" in
            [Yy]* )
                while true; do
                    read -p "📂 Enter the path to your existing $DB_NAME database (eg. /path/to/database_storage): " DB_PATH
                    if [[ -d "$DB_PATH" || -f "$DB_PATH" ]]; then
                        DATABASE_PATHS[$DB_VAR_NAME]="$DB_PATH"
                        echo "✅ $DB_NAME path set to: $DB_PATH"
                        return  # Exit the function immediately after successful input
                    else
                        echo "⚠️ The provided path does not exist or is empty. Please check and try again."
                        read -p "Do you want to re-enter the path (r) or install $DB_NAME instead (i)? (r/i): " RETRY
                        if [[ "$RETRY" == "i" ]]; then
                            break  # Exit inner loop to start installation
                        fi
                    fi
                done
                if [[ "$RETRY" == "i" ]]; then
                    break  # Exit outer loop to install the database
                fi
                ;;
            [Nn]* )
                read -p "📂 Enter the directory where you want to install $DB_NAME: " DB_PATH
                install_database "$DB_NAME" "$DB_VAR_NAME" "$DB_PATH"
                return  # Exit function after installation
                ;;
            * ) echo "⚠️ Please enter 'y(es)' or 'n(o)'.";;
        esac
    done
}

# Install databases in the specified directory
install_database() {
    local DB_NAME="$1"
    local DB_VAR_NAME="$2"
    local INSTALL_DIR="$3"
    local FINAL_DB_PATH="$INSTALL_DIR/${DB_SUBDIRS[$DB_VAR_NAME]}"

    echo "🚀 Installing $DB_NAME database in: $FINAL_DB_PATH"	

    case "$DB_VAR_NAME" in
        "DATABASE_1_PATH")
            wget -c https://repository1.com/database_1.tar.gz -P $INSTALL_DIR
            mkdir -p $FINAL_DB_PATH
	        tar -xzf "$INSTALL_DIR/database_1.tar.gz" -C "$FINAL_DB_PATH"
            echo "✅ Database 1 installed successfully!"
            ;;
        "DATABASE_2_PATH")
            wget https://repository2.com/database_2.tar.gz -P $INSTALL_DIR
	        mkdir -p $FINAL_DB_PATH
            tar -xzf "$INSTALL_DIR/database_2.tar.gz" -C "$FINAL_DB_PATH"
            echo "✅ Database 2 installed successfully!"
            ;;
        *)
            echo "⚠️ Unknown database: $DB_NAME"
            ;;
    esac

    DATABASE_PATHS[$DB_VAR_NAME]="$FINAL_DB_PATH"
}

# --- Initialize setup ---

show_welcome

# Set working directories
MODULE_WORK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
read -p "Enter the working directory (Press Enter for default: $MODULE_WORK_DIR): " USER_WORK_DIR
SETUP_WORK_DIR="$(realpath "${USER_WORK_DIR:-$MODULE_WORK_DIR}")"
echo "Working directory set to: $SETUP_WORK_DIR"

# --- Install conda environments ---

cd $MODULE_WORK_DIR
DEFAULT_CONDA_ENV_DIR=$(conda info --base)/envs

# Find or install...

# ...module environment
find_install_camp_env

# ...auxiliary environments
find_install_conda_env "multiqc" "MultiQC"

# --- Download databases ---

# Default database locations relative to $INSTALL_DIR
declare -A DB_SUBDIRS=(
    ["HOST_REF_PATH"]=""
)

# Absolute database paths (to be set in install_database)
declare -A DATABASE_PATHS

# Ask for host reference genome, if necessary
read -p "❓ Would you like to remove host reads? (y/n): " REMOVE_RESPONSE
case "$REMOVE_RESPONSE" in
    [Yy]* )
        HOST_FILTER="True"
        while true; do
            read -p "❓ Have you already downloaded your host's reference genome? (y/n): " DOWNLOAD_RESPONSE
            case "$DOWNLOAD_RESPONSE" in
                [Yy]* )
                    while true; do
                        read -p "📂 Enter the path to your host's reference genome: " HOST_REF_PATH
                        if [[ -d "$HOST_REF_PATH" || -f "$HOST_REF_PATH" ]]; then
                            DATABASE_PATHS["HOST_REF_PATH"]="$HOST_REF_PATH"
                            echo "✅ Host reference path set to: $HOST_REF_PATH"
                            break  # Exit inner loop after successful input
                        else
                            echo "⚠️ The provided path does not exist or is empty. Please check and try again."
                        fi
                    done
                    break  # Exit outer loop after successful input
                    ;;
                [Nn]* )
                    read -p "📂 Enter the directory where you want to download the host's reference genome: " HOST_REF_DIR
                    read -p "🌐 Enter the FTP site where you can download the host's reference genome from: " HOST_FTP_SITE
                    if [[ "$HOST_FTP_SITE" =~ ^ftp:// ]]; then
                        mkdir -p "$HOST_REF_DIR"
                        cd $HOST_REF_DIR
                        wget -c "$HOST_FTP_SITE" -P "$HOST_REF_DIR"
                        HOST_REF_PATH="$HOST_REF_DIR/$(basename "$HOST_FTP_SITE" .tar.gz)"
                        tar -xzf "$HOST_REF_PATH/$(basename "$HOST_FTP_SITE")" -C "$HOST_REF_PATH"
                        DATABASE_PATHS["HOST_REF_PATH"]="$HOST_REF_PATH"
                        echo "✅ Host reference genome downloaded successfully!"
                    else
                        DATABASE_PATHS["HOST_REF_PATH"]=""
                        echo "⚠️ Invalid FTP site- please download the host's reference genome manually and add its location to configs/parameters.yaml."
                    fi
                    break  # Exit outer loop after installation
                    ;;
                * ) echo "⚠️ Please enter 'y(es)' or 'n(o)'.";;
            esac
        done
        if [[ "$RETRY" == "i" ]]; then
            break  # Exit outer loop to install the database
        fi
        ;;
    [Nn]* )
        HOST_FILTER="False"
        DATABASE_PATHS["HOST_REF_PATH"]=""
        echo "🚫 Skipping host read removal."
        ;;
    * ) echo "⚠️ Please enter 'y(es)' or 'n(o)'.";;
esac

echo "✅ Database and environment setup complete!"

# --- Generate parameter configs ---

# Create test_data/parameters.yaml
PARAMS_FILE="$MODULE_WORK_DIR/test_data/parameters.yaml" 

echo "🚀 Generating test_data/parameters.yaml in $PARAMS_FILE ..."

# Default values for analysis parameters
SOME_CONSTANT=100
OTHER_CONSTANT=1000

# Use existing paths from DATABASE_PATHS
EXT_PATH="$MODULE_WORK_DIR/workflow/ext"  # Assuming extensions are in workflow/ext
LOW_QUAL_THRESHOLD=8
USE_HOST_FILTER="$HOST_FILTER"
HOST_GENOME_LOCATION="${DATABASE_PATHS[HOST_REF_PATH]}"

# Create test_data/parameters.yaml
cat <<EOL > "$PARAMS_FILE"
#'''Parameters config.'''#


# --- general --- #

ext:            '$EXT_PATH'
conda_prefix:   '$DEFAULT_CONDA_ENV_DIR'


# --- filter_lowqual_reads --- #

quality:        '$LOW_QUAL_THRESHOLD'


# --- filter_host_reads --- #

use_host_filter: False
host_genome:    ''
EOL

echo "✅ Test data configuration file created at: $PARAMS_FILE"
 
# Create configs/parameters.yaml 
PARAMS_FILE="$MODULE_WORK_DIR/configs/parameters.yaml"

cat <<EOL > "$PARAMS_FILE"
#'''Parameters config.'''#

# --- general --- #

ext:            '$EXT_PATH'
conda_prefix:   '$DEFAULT_CONDA_ENV_DIR'


# --- filter_lowqual_reads --- #

quality:        $LOW_QUAL_THRESHOLD


# --- filter_host_reads --- #

use_host_filter: $HOST_FILTER
host_genome:    '$HOST_GENOME_LOCATION'
EOL

echo "✅ Default configuration file created at: $PARAMS_FILE"

# --- Generate test data input CSV ---

# Create test_data/samples.csv
INPUT_CSV="$MODULE_WORK_DIR/test_data/samples.csv" 

echo "🚀 Generating test_data/samples.csv in $INPUT_CSV ..."

cat <<EOL > "$INPUT_CSV"
sample_name,fastq
uhgg,$MODULE_WORK_DIR/test_data/uhgg.fastq.gz

EOL

echo "✅ Test data input CSV created at: $INPUT_CSV"

echo "🎯 Setup complete! You can now test the workflow using `python $MODULE_WORK_DIR/workflow/nanopore-quality-control.py test`"

