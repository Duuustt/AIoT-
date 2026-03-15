# 配置文件

# MQTT 配置
MQTT_BROKER = "120.26.228.170"
MQTT_PORT = 1883
MQTT_TOPIC = "device/image"

# 支持设备列表
DEVICE_LIST = ["device001", "device002", "device003"]

# 数据库配置
USE_DB = False  # True: 启用数据库，False: 不接数据库
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "你的密码",
    "database": "device_data"
}

# YOLO 模型路径
YOLO_MODEL_PATH = "yolov8n.pt"
