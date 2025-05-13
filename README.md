# Nanopore Long-Read Quality Control

![image](https://img.shields.io/badge/version-0.3.0-brightgreen)

<!-- [![Documentation Status](https://readthedocs.org/projects/camp-nanopore-quality-control/badge/?version=latest)](https://camp-nanopore-quality-control.readthedocs.io/en/latest/?version=latest) -->
<!-- [![Documentation Status](https://img.shields.io/badge/docs-unknown-yellow.svg)]() -->

## Overview

This module is designed to function as both a standalone MAG Nanopore quality control pipeline as well as a component of the larger CAMP metagenome analysis pipeline. As such, it is both self-contained (ex. instructions included for the setup of a versioned environment, etc.), and seamlessly compatible with other CAMP modules (ex. ingests and spawns standardized input/output config files, etc.).

The CAMP Nanopore quality control module performs initial QC on raw input reads, including read trimming, read filtering, and removal of host reads.

## Installation

> [!TIP]
> All databases used in CAMP modules will also be available for download on Zenodo (link TBD).

### Install `conda`

If you don't already have `conda` handy, we recommend installing `miniforge`, which is a minimal conda installer that, by default, installs packages from open-source community-driven channels such as `conda-forge`.
```Bash
# If you don't already have conda on your system...
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
```

Run the following command to initialize Conda for your shell. This will configure your shell to recognize conda activate. 
```Bash
conda init
```

Restart your terminal or run:
```Bash
source ~/.bashrc  # For bash users
source ~/.zshrc   # For zsh users
```
### Setting up the Nanopore Long-Read QC Module

1.  Clone repo from [Github](https://github.com/Meta-CAMP/camp_nanopore-quality-control).
```Bash
git clone https://github.com/Meta-CAMP/camp_nanopore-quality-control
```

2. Set up the rest of the module interactively by running `setup.sh`. This step downloads the host reference genome (if host read removal is reuiqred) and installs the other conda environments needed for running the module. This is done interactively by running `setup.sh`. `setup.sh` also generates `parameters.yaml` based on user input paths for running this module.
```Bash
cd camp_nanopore-quality-control/
source setup.sh

# If you encounter issues where conda activate is not recognized, follow these steps to properly initialize Conda
conda init
source ~/.bashrc # or source ~/.zshrc
```

4. Make sure the installed pipeline works correctly. 
<!--- 
Add runtime information of the module on the test dataset here. For example: With X threads and a maximum of Y GB allocated, the dataset should finish in approximately Z minutes.
--->
```Bash
# Run tests on the included sample dataset
conda activate camp
python /path/to/camp_nanopore-quality-control/workflow/nanopore-quality-control.py test
```

## Using the Module

**Input**: `/path/to/samples.csv` provided by the user.

<!-- Add description of your workflow's output files -->

**Structure**: 
```
└── workflow
    ├── Snakefile
    ├── nanopore-quality-control.py
    ├── utils.py
    ├── __init__.py
```

- `workflow/nanopore-quality-control.py`: Click-based CLI that wraps the `snakemake` and unit test generation commands for clean management of parameters, resources, and environment variables. 
- `workflow/Snakefile`: The `snakemake` pipeline. 
- `workflow/utils.py`: Sample ingestion and work directory setup functions, and other utility functions used in the pipeline and the CLI.

1.  Make your own `samples.csv` based on the template in `configs/samples.csv`. Sample test data can be found in `test_data/`.  
    -   `ingest_samples` in `workflow/utils.py` expects Illumina reads in FastQ (may be gzipped) form and de novo assembled contigs in FastA form
    -   `samples.csv` requires either absolute paths or paths relative to the directory that the module is being run in

2.  Update the relevant parameters in `configs/parameters.yaml`.

3.  Update the computational resources available to the pipeline in `resources.yaml`.

4. To run CAMP on the command line, use the following, where `/path/to/work/dir` is replaced with the absolute path of your chosen working directory, and `/path/to/samples.csv` is replaced with your copy of `samples.csv`.  
    - The default number of cores available to Snakemake is 1 which is enough for test data, but should probably be adjusted to 10+ for a real dataset.
   -   Relative or absolute paths to the Snakefile and/or the working directory (if you're running elsewhere) are accepted!
```Bash
    conda activate camp
    python /path/to/camp_nanopore-quality-control/workflow/nanopore-quality-control.py \
        (-c max_number_of_local_cpu_cores) \
        -d /path/to/work/dir \
        -s /path/to/samples.csv
```
-   Note: This setup allows the main Snakefile to live outside of the
    work directory.

5. To run CAMP on a job submission cluster (for now, only Slurm is supported), use the following.  
    - `--slurm` is an optional flag that submits all rules in the Snakemake pipeline as `sbatch` jobs.
   - In Slurm mode, the `-c` flag refers to the maximum number of `sbatch` jobs submitted in parallel, **not** the pool of cores available to run the jobs. Each job will request the number of cores specified by threads in `configs/resources/slurm.yaml`.
```Bash
    conda activate camp
    sbatch -J jobname -o jobname.log << "EOF"
    #!/bin/bash
    python /path/to/camp_nanopore-quality-control/workflow/nanopore-quality-control.py --slurm \
        (-c max_number_of_parallel_jobs_submitted) \
        -d /path/to/work/dir \
        -s /path/to/samples.csv
    EOF
```

# Credits

-   This package was created with
    [Cookiecutter](https://github.com/cookiecutter/cookiecutter) as a simplified version of the [project template](https://github.com/audreyr/cookiecutter-pypackage).
-   Free software: MIT License
-   Documentation: <https://nanopore-quality-control.readthedocs.io>.
