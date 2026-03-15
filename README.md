# AIoT-RealTime-Detection: 基于 YOLOv8 & MQTT 的实时监控识别系统

## 1. 项目简介

本项目是一套完整的 **AIoT (人工智能物联网)** 解决方案，实现了从边缘端图像采集到云端深度学习推理，再到 Web 端实时可视化展示的全链路功能。系统采用轻量级通信协议与异步高并发架构，能够有效解决多摄像头监控场景下的数据传输实时性与识别准确性问题。

## 2. 系统架构

系统由四个核心模块组成：

1. **边缘端 (Edge)**：通过 `camera_upload.py` 采集 OpenCV 视频流，将图像进行 Base64 编码并利用 **MQTT 协议** 异步推送到云端。
2. **消息中枢 (Broker)**：采用 **EMQX** 作为消息代理，处理高并发的图像数据流。
3. **云端推理中心 (Server)**：
* `mqtt_client.py` 接收数据并解码。
* `yolo_detector.py` 调用 **YOLOv8** 模型进行目标检测。
* `db_utils.py` 可选地将检测结果持久化至 MySQL。


4. **展示层 (Frontend)**：基于 **FastAPI** 构建后端接口，Web 前端通过 AJAX 定时轮询实现监控画面的“伪直播”展示与目标列表更新。

## 3. 技术栈

* **深度学习**：PyTorch, YOLOv8 (Ultralytics)
* **后端框架**：FastAPI, Uvicorn
* **物联网通信**：MQTT (Paho-MQTT), Base64 编码
* **图像处理**：OpenCV, Pillow
* **前端技术**：HTML5, CSS3 (Flexbox/Grid), JavaScript

## 4. 核心功能与亮点

* **异步高并发**：利用 Python 线程池（Threading）并行运行 MQTT 接收服务与 FastAPI Web 服务，互不干扰。
* **轻量化传输**：优化了 MQTT 载荷结构，通过 JSON 封装设备 ID 与图像数据，支持多设备（device001, device002...）接入。
* **实时检测与标注**：服务端动态生成带边界框（Bounding Box）和置信度标签的标注图，并实时推送到前端。
* **跨平台部署**：支持在阿里云等 Linux 服务器上运行，具备完整的端口与权限管理方案。

## 5. 项目结构说明

```text
├── camera_upload.py    # 客户端：摄像头采集与发送
├── mqtt_client.py      # 服务端：MQTT 监听与检测流转
├── yolo_detector.py    # 算法层：YOLOv8 模型推理逻辑
├── main.py             # 入口文件：多线程启动服务
├── frontend_server.py  # 接口层：FastAPI 路由定义
├── config.py           # 配置层：服务器IP、端口及模型路径
├── db_utils.py         # 存储层：MySQL 数据库操作
├── static/             # 静态资源 (CSS)
└── templates/          # 前端页面 (HTML)

```

## 6. 快速开始

### 6.1 环境准备

```bash
pip install ultralytics paho-mqtt fastapi uvicorn opencv-python mysql-connector-python

```

### 6.2 配置文件

修改 `config.py` 中的 `MQTT_BROKER` 为你的服务器 IP 地址。

### 6.3 运行

1. **启动服务端**（包含云端推理与 Web 服务）：
```bash
python main.py

```


2. **启动边缘端**（连接摄像头）：
```bash
python camera_upload.py

```


3. **访问页面**：
打开浏览器访问 `http://你的服务器IP:8080` 查看实时监控仪表板。

## 7. 运行效果展示

### 7.1 实时监控仪表板
Web 前端实时同步云端识别结果，左侧为带有人脸/目标标注框的视频流，右侧实时刷新检测到的目标列表及置信度。

![Web Dashboard](./dashboard.png)



### 7.2 后端推理日志
展示云服务器端 MQTT 接收、Base64 解码以及 YOLOv8 毫秒级推理的实时过程。

![Terminal Log](./terminal.png)

---

