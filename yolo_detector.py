import cv2
import numpy as np
from ultralytics import YOLO
from config import YOLO_MODEL_PATH

model = YOLO(YOLO_MODEL_PATH)

def detect_image(image_bytes):
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    results = model(img)[0]

    detection_result = []
    for r in results.boxes.data.tolist():
        x1, y1, x2, y2, score, cls = r
        detection_result.append({
            "bbox": [x1, y1, x2, y2],
            "confidence": float(score),
            "class": int(cls)
        })
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0,255,0), 2)

    # 转为 bytes
    _, buffer_det = cv2.imencode('.jpg', img)
    return detection_result, image_bytes, buffer_det.tobytes()
