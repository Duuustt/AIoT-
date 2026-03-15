import cv2
import base64
import json
import time
import paho.mqtt.client as mqtt
from config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC

DEVICE_ID = "device001"  # 可改 device002/device003

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        _, buffer = cv2.imencode('.jpg', frame)
        img_b64 = base64.b64encode(buffer).decode()

        payload = {
            "device_id": DEVICE_ID,
            "image": img_b64
        }

        client.publish(MQTT_TOPIC, json.dumps(payload))
        print(f"已上传 {DEVICE_ID} 图像")
        time.sleep(2)
except KeyboardInterrupt:
    cap.release()
    client.disconnect()
