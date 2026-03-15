from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from mqtt_client import latest_images, DEVICE_LIST
import db_utils  # 新增: 导入数据库工具
import time
from datetime import datetime
import base64  # 新增: 用于 BLOB 到 Base64 的转换

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设备状态跟踪
device_status = {device_id: {"status": "offline", "last_update": 0} for device_id in DEVICE_LIST}


def update_device_status(device_id):
    """更新设备状态"""
    current_time = time.time()
    if device_id in latest_images:
        device_status[device_id] = {
            "status": "online",
            "last_update": current_time
        }
    else:
        # 如果超过30秒没有更新，标记为离线
        if current_time - device_status[device_id]["last_update"] > 30:
            device_status[device_id]["status"] = "offline"


start_time = time.time()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """主页面"""
    # 更新所有设备状态
    for device_id in DEVICE_LIST:
        update_device_status(device_id)

    return templates.TemplateResponse("index.html", {"request": request, "device_list": DEVICE_LIST})


@app.get("/api/latest/{device_id}")
def get_latest_data(device_id: str):
    """获取指定设备的最新检测数据和图像"""
    update_device_status(device_id)
    status_info = device_status[device_id]

    detection_data = {}
    if status_info["status"] == "online":
        # 从内存中获取最新数据
        detection_data = {
            "image_b64": base64.b64encode(latest_images[device_id]["detection_image"]).decode('utf-8'),
            "detection": latest_images[device_id]["result"]
        }

    return {
        "success": True,
        "device_id": device_id,
        "status": status_info["status"],
        "last_update": status_info["last_update"],
        "is_online": status_info["status"] == "online",
        "detection_data": detection_data
    }


@app.get("/api/history")
def get_history(limit: int = 20):
    """获取最新的历史检测记录"""
    try:
        # 调用 db_utils 中已有的 fetch_history 函数
        history_data = db_utils.fetch_history(limit=limit)

        # 处理二进制图像数据：将 BLOB 转换为 Base64 字符串
        formatted_history = []
        for item in history_data:
            # 原始图像和检测图像的 BLOB 数据需要转为 Base64 字符串
            # 假设存储的是 JPEG 格式
            # 注意: item['original_image'] 和 item['detection_image'] 现在是 bytes 类型
            item['original_image_b64'] = base64.b64encode(item['original_image']).decode('utf-8')
            item['detection_image_b64'] = base64.b64encode(item['detection_image']).decode('utf-8')

            # 删除原始的二进制字段，避免传输过大
            del item['original_image']
            del item['detection_image']

            # 格式化时间戳 (假设 item['timestamp'] 是 datetime 对象)
            item['timestamp_str'] = item['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            del item['timestamp']

            # 确保 result 字段是 JSON 对象，db_utils 已经处理了

            formatted_history.append(item)

        return JSONResponse(content={
            "success": True,
            "data": formatted_history
        })
    except Exception as e:
        print(f"获取历史数据失败: {e}")
        return JSONResponse(content={"success": False, "message": "无法连接或查询数据库"}, status_code=500)


@app.get("/api/stats")
def get_system_stats():
    """获取系统统计信息"""
    # 更新所有设备状态
    for device_id in DEVICE_LIST:
        update_device_status(device_id)

    online_count = sum(1 for device_id in DEVICE_LIST if device_status[device_id]["status"] == "online")
    total_detections = sum(len(latest_images[device_id]["result"]) for device_id in latest_images)

    return {
        "success": True,
        "total_devices": len(DEVICE_LIST),
        "online_devices": online_count,
        "offline_devices": len(DEVICE_LIST) - online_count,
        "total_detections": total_detections,
        "latest_update": max(
            device_status[device_id]["last_update"] for device_id in DEVICE_LIST) if DEVICE_LIST else 0,
        "system_uptime": time.time() - start_time
    }


@app.get("/health")
def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "devices_configured": len(DEVICE_LIST)
    }