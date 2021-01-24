# All the commands below should be run on host machine

# Remove any previous installation of nvidia drivers and libs
# This is due to Tensorflow 2.0.0 requiring specific versions

apt-get purge -y *nvidia*
apt-get autoremove -y

apt-get update
apt-get install -y wget gnupg2
rm -rf /var/lib/apt/lists/*

update-initramfs -u

# Get Cuda repository and install Cuda toolkit

wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-repo-ubuntu1804_10.0.130-1_amd64.deb
dpkg -i cuda-repo-ubuntu1804_10.0.130-1_amd64.deb
apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub
apt-get update
wget http://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64/nvidia-machine-learning-repo-ubuntu1804_1.0.0-1_amd64.deb

# Install Nvidia Driver version 455

sudo apt-get -y install nvidia-driver-455

# Install Container toolkit to support sharing GPU devices to Docker

apt-get -y install nvidia-container-toolkit
systemctl restart docker

apt-get install ./nvidia-machine-learning-repo-ubuntu1804_1.0.0-1_amd64.deb
apt-get update

# Install additional libs

apt-get install -y --allow-downgrades --allow-change-held-packages libcudnn7=7.6.5.32-1+cuda10.0 libcudnn7-dev=7.6.5.32-1+cuda10.0
apt-mark hold libcudnn7=7.6.5.32-1+cuda10.0 libcudnn7-dev=7.6.5.32-1+cuda10.0

# Create NVIDIA runtime

echo "
{"graph": "/opt/docker",
    "default-runtime": "nvidia",
        "runtimes": {
            "nvidia": {
                "path": "nvidia-container-runtime",
                "runtimeArgs": []
            }
        }
}
" > /etc/docker/daemon.json
