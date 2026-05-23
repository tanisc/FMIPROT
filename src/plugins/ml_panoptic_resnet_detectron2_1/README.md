# ML Panoptic ResNet Detectron2 Plugin

> **Warning:** This plugin works in Linux only. There is no Windows support.

## Installation & Setup

**1. Create and activate a new conda environment:**

```bash
conda create -n fpn_det2 python=3
conda activate fpn_det2
```

**2. Configure PyTorch installation:**

Edit `detectron2_install.sh` to set the `index-url` for the PyTorch installation according to the desired version (CPU or GPU). You can get the correct version from [PyTorch's Getting Started page](https://pytorch.org/get-started/locally/).

Edit this line:
```
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**3. Install Detectron2 and PyTorch:**

```bash
bash detectron2_install.sh
```
*Note: Make sure that the installation script prints the PyTorch and Detectron2 versions.*

**4. Provide the Python path:**

Edit `ml_panoptic_resnet_detectron2_1.sh` to provide the Python path for the newly created conda environment.

Edit this line:
```bash
PYTHON=/FMIprot/srcrun/miniconda3/envs/fpn_det2/bin/python
```

The python path can be found by running (when the conda environment is activated)
```
which python
```

**5. Provide the Detectron2 path:**

Edit `ml_panoptic_resnet_detectron2_1.py` to provide the Detectron2 path created after the installation. Normally, it should be under the plugin directory.

Edit this line:
```python
sys.path.insert(0, os.path.abspath('/FMIprot/srcrun/master_report/src/plugins/ml_panoptic_resnet_detectron2_1/detectron2'))
```

**6. Download the model files:**

Download the model files from [FMIprot ML Models](https://fmiprot.fmi.fi/index.php?page=ML%20Models) and extract them into the plugin folder, so that the structure is:

```text
src/plugins/ml_panoptic_resnet_detectron2_1
├── detectron2
│   ├── configs
│   ├── datasets
│   ├── demo
│   ├── detectron2
│   ├── dev
│   ├── docker
│   ├── docs
│   ├── GETTING_STARTED.md
│   ├── INSTALL.md
│   ├── LICENSE
│   ├── MODEL_ZOO.md
│   ├── projects
│   ├── README.md
│   ├── setup.cfg
│   ├── setup.py
│   ├── tests
│   └── tools
├── detectron2_install.py
├── detectron2_install.sh
├── ml_panoptic_resnet_detectron2_1.py
├── ml_panoptic_resnet_detectron2_1.sh
├── model
│   ├── categories.json
│   ├── config.yaml
│   ├── last_checkpoint
│   ├── log.txt
│   ├── metrics.json
│   ├── model_final.pth
│   └── panoptic_evaluation
└── README.md
```






