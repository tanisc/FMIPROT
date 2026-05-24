# Custom ANN model for 3 class snow cover monitoring dense mode Plugin

> **Warning:** This plugin works in Linux only. There is no Windows support.

## Installation & Setup

**1. Create and activate a new conda environment:**

You can create the required environment using the provided `conda_env.yml` file:

```bash
conda env create -f conda_env.yml
conda activate fsc_ml
```
*Note: The environment name specified in the file is `fsc_ml`.*

**2. Provide the Python path:**

Edit `ml_ann_3_dense_reg_1.sh` to provide the Python path for the newly created conda environment.

Edit this line:
```bash
PYTHON=/FMIprot/srcrun/miniconda3/envs/fsc_ml/bin/python
```

The python path can be found by running (when the conda environment is activated):
```bash
which python
```

**3. Download the model files:**

Download the model files from [FMIprot ML Models](https://fmiprot.fmi.fi/index.php?page=ML%20Models) and place them into the `models` directory so that the script can load the Keras model. 

Your directory structure should look like this:

```text
src/plugins/ml_ann_3_dense_reg_1
├── conda_env.yml
├── ml_ann_3_dense_reg_1.py
├── ml_ann_3_dense_reg_1.sh
├── models
│   ├── 3_ConVlayer_adam
│   ├── 3_dense_reg
│   ├── cropped_3
│   ├── Dense_only
│   ├── large_kernels_Monimet
│   └── one_dense_layer
└── README.md
```
