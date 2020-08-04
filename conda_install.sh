conda create --name fmiprot python=2.7
conda activate fmiprot
conda config --add channels conda-forge
conda config --add channels alges
conda install --file requirements_linux-64.txt
