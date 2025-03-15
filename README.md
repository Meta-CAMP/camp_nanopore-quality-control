# Nanopore Long-Read Quality Control

[![Documentation Status](https://img.shields.io/badge/docs-unknown-yellow.svg)]() ![image](https://img.shields.io/badge/version-0.1.0-brightgreen)

<!-- [![Documentation Status](https://readthedocs.org/projects/camp-nanopore-quality-control/badge/?version=latest)](https://camp-nanopore-quality-control.readthedocs.io/en/latest/?version=latest) -->

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

2. Set up the conda environment (contains Snakemake, Click, and other essentials) using `configs/conda/nanopore-quality-control.yaml`. 
```Bash
# Create and activate conda environment 
cd camp_nanopore-quality-control
conda env create -f configs/conda/nanopore-quality-control.yaml
conda activate nanopore_quality_control
```

3. Set up the rest of the module interactively by running `setup.sh`. This step downloads the host reference genome (if host read removal is reuiqred) and installs the other conda environments needed for running the module. This is done interactively by running `setup.sh`. `setup.sh` also generates `parameters.yaml` based on user input paths for running this module.
```Bash
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
python /path/to/camp_nanopore-quality-control/workflow/nanopore-quality-control.py test
```

## Using the Module

**Input**: `/path/to/samples.csv` provided by the user.

**Output**: 1) An output config file summarizing 2) the module's outputs.

- `/path/to/work/dir/nanopore-quality-control/final_reports/samples.csv` for ingestion by the next module (ex. quality-checking)

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

```
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

```
    sbatch -J jobname -o jobname.log << "EOF"
    #!/bin/bash
    python /path/to/camp_nanopore-quality-control/workflow/nanopore-quality-control.py --slurm \
        (-c max_number_of_parallel_jobs_submitted) \
        -d /path/to/work/dir \
        -s /path/to/samples.csv
    EOF
```

# Extending the Module

We love to see it! This module was partially envisioned as a dependable, prepackaged sandbox for developers to test their shiny new tools in.

These instructions are meant for developers who have made a tool and want to integrate or demo its functionality as part of the standard Nanopore quality control workflow, or developers who want to integrate an existing tool.

1.  Write a module rule that wraps your tool and integrates its input and output into the pipeline.  
    -   This is a great [Snakemake tutorial](https://bluegenes.github.io/hpc-snakemake-tips/) for writing basic Snakemake rules.
    -   If you're adding new tools from an existing YAML, use `conda env update --file configs/conda/existing.yaml --prune`.
    -   If you're using external scripts and resource files that i) cannot easily be integrated into either utils.py or parameters.yaml, and ii) are not as large as databases that would justify an externally stored download, add them to `workflow/ext/` or `workflow/ext/scripts` and use `rule external_rule` as a template to wrap them.

2.  Update the `make_config` in `workflow/Snakefile` rule to check for your tool's output files. Update `samples.csv` to document its output if downstream modules/tools are meant to ingest it.  
    - If you plan to integrate multiple tools into the module that serve the same purpose but with different input or output requirements (ex. for alignment, Minimap2 for Nanopore reads vs. Bowtie2 for Illumina reads), you can toggle between these different 'streams' by setting the final files expected by `make_config` using the example function `workflow_mode`.
    - Update the description of the `samples.csv` input fields in the CLI script `workflow/nanopore-quality-control.py`.

3.  If applicable, update the default conda config using `conda env export > config/conda/nanopore-quality-control.yaml` with your tool and its dependencies.  
    -   If there are dependency conflicts, make a new conda YAML under `configs/conda` and specify its usage in specific rules using the `conda` option (see `first_rule` for an example).

4.  Add your tool's installation and running instructions to the module documentation and (if applicable) add the repo to your [Read the Docs account](https://readthedocs.org/) + turn on the Read the Docs service hook.

5. Run the pipeline once through to make sure everything works using the test data in `test_data/` if appropriate, or your own appropriately-sized test data. Then, generate unit tests to ensure that others can sanity-check their installations.  
   - Note: Python functions imported from `utils.py` into `Snakefile` should be debugged on the command-line first before being added to a rule because Snakemake doesn't port standard output/error well when using `run:`.

```
    python /path/to/camp_nanopore-quality-control/workflow/nanopore-quality-control.py (--unit_test) \
        -d /path/to/work/dir \
        -s /path/to/samples.csv
```

1. Increment the version number of the modular pipeline. :
```
    bump2version --allow-dirty --commit --tag major workflow/__init__.py \
                 --current-version A.C.E --new-version B.D.F
```

1.  If you want your tool integrated into the main CAMP pipeline, send a pull request and we'll have a look at it ASAP!  
    -   Please make it clear what your tool intends to do by including a summary in the commit/pull request (ex. "Release X.Y.Z: Integration of tool A, which does B to C and outputs D").

 <!-- Bugs ----Put known ongoing problems here  -->
# Credits

-   This package was created with
    [Cookiecutter](https://github.com/cookiecutter/cookiecutter) as a simplified version of the [project template](https://github.com/audreyr/cookiecutter-pypackage).
-   Free software: MIT License
-   Documentation: <https://nanopore-quality-control.readthedocs.io>.
