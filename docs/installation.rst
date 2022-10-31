.. highlight:: shell

============
Installation
============


Stable release
--------------

1. Clone repo from `github <https://github.com/michaeltoomey/camp_nanopore-quality-control>_`. 

2. Set up the conda environment (contains, Snakemake) using ``configs/conda/camp_nanopore-quality-control.yaml``. 

3. Make sure the installed pipeline works correctly. ``pytest`` only generates temporary outputs so no files should be created.
::
    cd camp_nanopore-quality-control
    conda env create -f configs/conda/camp_nanopore-quality-control.yaml
    conda activate camp_nanopore-quality-control
    pytest .tests/unit/

