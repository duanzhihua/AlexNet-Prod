# 安装说明

* 下载代码库

```shell
git clone https://github.com/littletomatodonkey/AlexNet-Prod.git
```

* 进入文件夹，安装requirements

```shell
pip3.7 install -r requirements.txt
```

* 安装PaddlePaddle与PyTorch

```shell
# CPU版本的PaddlePaddle
pip3.7 install paddlepaddle==2.2.0
# 如果希望安装GPU版本的PaddlePaddle，可以使用下面的命令
# python -m pip install paddlepaddle-gpu==2.2.0
# 安装PyTorch
pip3.7 install torch
```

* 验证PaddlePaddle是否安装成功

运行python，输入下面的命令。

```shell
import paddle
paddle.utils.run_check()
```

如果输出下面的内容，则说明PaddlePaddle安装成功。

```
PaddlePaddle is installed successfully! Let's start deep learning with PaddlePaddle now.
```


* 验证PyTorch是否安装成功

运行python，输入下面的命令，如果可以正常输出，则说明torch安装成功。

```shell
import torch
print(torch.__version__)
# 如果安装的是cpu版本，可以按照下面的命令确认torch是否安装成功
# 期望输出为 tensor([1.])
print(torch.Tensor([1.0]))
# 如果安装的是gpu版本，可以按照下面的命令确认torch是否安装成功
# 期望输出为 tensor([1.], device='cuda:0')
print(torch.Tensor([1.0]).cuda())
```

# Reference

* torchvision：https://github.com/pytorch/vision （该项目中AlexNet的参考实现来源）