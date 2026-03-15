import threading
from mqtt_client import start_mqtt
import uvicorn
from frontend_server import app

def run_frontend():
    # 启动 FastAPI 前端服务
    uvicorn.run(app, host="0.0.0.0", port=8080)

def run_mqtt():
    # 启动 MQTT 接收服务
    start_mqtt()

if __name__ == "__main__":
    # 创建线程
    mqtt_thread = threading.Thread(target=run_mqtt, daemon=True)
    frontend_thread = threading.Thread(target=run_frontend, daemon=True)

    # 启动线程
    mqtt_thread.start()
    frontend_thread.start()

    print("项目已启动，前端: http://120.26.228.170:8080/")
    print("按 Ctrl+C 停止")

    # 主线程保持运行
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("项目停止")
