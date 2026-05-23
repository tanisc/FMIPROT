# conda create -n fpn_det2 python=3
# conda activate fpn_det2

read -p "Did you activate the environment (y/n)?" CONT
if [ "$CONT" != "y" ]; then
    exit 1
fi

# pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip3 install tqdm
python3 detectron2_install.py

# export DISPLAY=$(ip route list default | awk '{print $3}'):0