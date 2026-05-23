# export LD_LIBRARY_PATH=/opt/rh/python27/root/usr/lib64/
PYTHON=/FMIprot/srcrun/miniconda3/envs/fsc_ml/bin/python
$PYTHON $(dirname $0)/ml_ann_3_dense_reg_1.py $1 $2
