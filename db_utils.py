import json
from config import USE_DB, DB_CONFIG
from datetime import datetime

if USE_DB:
    import mysql.connector



def insert_detection(device_id, result, original_image, detection_image, detection_time, summary):
    if not USE_DB:
        print(f"[模拟存储] {device_id} 检测到 {len(result)} 个目标，时间：{detection_time}")
        return
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        sql = "INSERT INTO detection_history (device_id, timestamp, result, summary, original_image, detection_image) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (
            device_id,
            detection_time,
            json.dumps(result, ensure_ascii=False),
            json.dumps(summary, ensure_ascii=False),
            original_image,
            detection_image
        ))

        conn.commit()

        print(f"[DB SUCCESS] {device_id} 的检测数据已成功保存到数据库。目标数: {len(result)}")

        cursor.close()
        conn.close()
    except Exception as e:
        print("数据库插入失败:", e)


def fetch_history(limit=10):
    if not USE_DB:
        return []
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM detection_history ORDER BY timestamp DESC LIMIT %s", (limit,))
        rows = cursor.fetchall()

        for row in rows:
            row["result"] = json.loads(row["result"])
            row["summary"] = json.loads(row["summary"])

        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        print("数据库查询失败:", e)
        return []


def fetch_latest(device_id):
    if not USE_DB:
        return {"result": [], "summary": {}, "original_image": b"", "detection_image": b""}
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM detection_history WHERE device_id=%s ORDER BY timestamp DESC LIMIT 1",
                       (device_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            row["result"] = json.loads(row["result"])
            row["summary"] = json.loads(row["summary"])
        return row
    except Exception as e:
        print("数据库查询失败:", e)
        return {"result": [], "summary": {}, "original_image": b"", "detection_image": b""}