import json
import base64
import paho.mqtt.client as mqtt
from config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, DEVICE_LIST
from yolo_detector import detect_image
from db_utils import insert_detection
from datetime import datetime

# YOLOv8 (COCO 80类) 标准类别映射表
# 类别ID (0-79) 对应名称
YOLO_COCO_CLASSES = {
    0: '人', 1: '自行车', 2: '汽车', 3: '摩托车', 4: '飞机', 5: '公交车', 6: '火车', 7: '卡车', 8: '船',
    9: '交通信号灯',
    10: '灭火栓', 11: '停车标志', 12: '停车计时器', 13: '长凳', 14: '鸟', 15: '猫', 16: '狗', 17: '马', 18: '羊',
    19: '牛',
    20: '大象', 21: '熊', 22: '斑马', 23: '长颈鹿', 24: '背包', 25: '伞', 26: '手提包', 27: '领带', 28: '手提箱',
    29: '飞盘',
    30: '滑雪板', 31: '运动雪橇', 32: '运动球', 33: '风筝', 34: '棒球棒', 35: '棒球手套', 36: '滑板', 37: '冲浪板',
    38: '网球拍', 39: '瓶子',
    40: '酒杯', 41: '杯子', 42: '叉子', 43: '刀', 44: '勺子', 45: '碗', 46: '香蕉', 47: '苹果', 48: '三明治',
    49: '橙子',
    50: '西兰花', 51: '胡萝卜', 52: '热狗', 53: '披萨', 54: '甜甜圈', 55: '蛋糕', 56: '椅子', 57: '沙发', 58: '盆栽',
    59: '床',
    60: '餐桌', 61: '马桶', 62: '电视', 63: '笔记本电脑', 64: '鼠标', 65: '遥控器', 66: '键盘', 67: '手机',
    68: '微波炉', 69: '烤箱',
    70: '烤面包机', 71: '水槽', 72: '冰箱', 73: '书', 74: '时钟', 75: '花瓶', 76: '剪刀', 77: '泰迪熊', 78: '吹风机',
    79: '牙刷'
}


latest_images = {}  # {device_id: {"result":[], "detection_image": bytes}}


def create_detection_summary(results):

    summary = {}
    for res in results:
        cls_id = int(res['class'])
        class_name = YOLO_COCO_CLASSES.get(cls_id, f"未知类别_{cls_id}")
        summary[class_name] = summary.get(class_name, 0) + 1
    return summary


def on_connect(client, userdata, flags, rc):
    print("MQTT 连接成功")
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        device_id = payload.get("device_id")
        if device_id not in DEVICE_LIST:
            print(f"未知设备 {device_id}，忽略数据")
            return

        img_b64 = payload.get("image")
        if not img_b64:
            return

        image_bytes = base64.b64decode(img_b64)
        result, original_img_bytes, detection_img = detect_image(image_bytes)

        detection_time = datetime.now()

        detection_summary = create_detection_summary(result)

        insert_detection(device_id, result, original_img_bytes, detection_img, detection_time, detection_summary)

        latest_images[device_id] = {
            "result": result,
            "detection_image": detection_img
        }

        print(f"{device_id} 图像识别完成，检测到 {len(result)} 个目标")

    except Exception as e:
        print("处理图像错误:", e)


def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()


if __name__ == "__main__":
    start_mqtt()