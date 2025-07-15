
# Could not load library libcudnn_ops_infer.so.8.
# Error: libcudnn_ops_infer.so.8: cannot open shared object file: No such file or directory

```
curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3bf863cc.pub | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-cuda-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/nvidia-cuda-keyring.gpg] https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/ /" | sudo tee /etc/apt/sources.list.d/nvidia-cuda.list
sudo apt update
sudo apt install libcudnn8 libcudnn8-dev
echo "/usr/lib/x86_64-linux-gnu" | sudo tee /etc/ld.so.conf.d/cudnn.conf
sudo ldconfig
```