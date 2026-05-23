import sys, os, distutils.core
os.system("python -m pip install pyyaml==5.1 opencv-python")
os.system("git clone 'https://github.com/facebookresearch/detectron2'")
dist = distutils.core.run_setup("./detectron2/setup.py")
os.system("python -m pip install " + ' '.join([f"'{x}'" for x in dist.install_requires]))
sys.path.insert(0, os.path.abspath('./detectron2'))
import detectron2, torch

TORCH_VERSION = ".".join(torch.__version__.split(".")[:2])
CUDA_VERSION = torch.__version__.split("+")[-1]
print("torch: ", TORCH_VERSION, "; cuda: ", CUDA_VERSION)
print("detectron2:", detectron2.__version__)
