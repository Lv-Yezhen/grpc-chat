# LYZ_CHAT

## 在 docoker 运行

在此文件夹终端中运行以下指令构建镜像,有时网络不好可以多试几次,详见 Dockerfile

```
docker build -t chat_image .
```

然后跑起三个实例,比如

```
docker run --name pc1 -it -v /Users/mac/Documents/volume:/path chat_image

docker run --name pc2 -it -v /Users/mac/Documents/volume:/path chat_image

docker run --name pc3 -it -v /Users/mac/Documents/volume:/path chat_image
```

在每一个容器的终端中使用运行程序

```
python3 main.py
```

## 在主机运行

确保安装 python 和 pip,并使用下面指令安装所有依赖

```
pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

然后使用 python 运行

```
python3 main.py
```

## 程序使用

运行后填入想要进行聊天的对等方 ip,可以输入多个

最后进入消息输入页面,从上往下依次是

- 此次聊天的所有消息
- 到各个对等方(如果有)的网络时延
- 请求消息输入框

当输入空白按下回车会刷新聊天消息显示

每次聊天记录会保存在 mes_set 的 mes.txt 中,旧的 mes 会被标记为 oldmes1.txt 等,每个对等方都会保留一份完整聊天记录

## 维护与更新

如果修改了 proto 文件,应该使用以下命令重新生成 py 文件(需确保安装了 grpc 依赖)

```
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./chat.proto
```

mes_set 里的文件需要定期清理
