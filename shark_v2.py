
import os
import configparser
from ultralytics import YOLO
from serial.tools import list_ports
import mediapipe as mp
import numpy as np
import cv2
import time
import serial
import torch

# ====================== Config System ======================
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.ini")

# 預設設定
DEFAULT_CONFIG = {
    "YOLO": {
        "MODEL": "best.pt",
        "CONF": "0.15",
        "IOU": "0.1",
        "IMGSZ": "640"
    },
    "CAMERA": {
        "INDEX": "1",
        "WIDTH": "1280",
        "HEIGHT": "720"
    },
    "HAND": {
        "DRAW": "True"
    },
    "ALERT": {
        "COOLDOWN_S": "0.7"
    },
    "SERIAL": {
        "BAUD": "115200"
    }
}

def create_default_config(path: str):
    """第一次執行時自動建立 config.ini"""
    config = configparser.ConfigParser()
    for section, values in DEFAULT_CONFIG.items():
        config[section] = values
    with open(path, "w", encoding="utf-8") as f:
        config.write(f)
    print(f"[INFO] 已建立預設設定檔: {path}")

# 如果設定檔不存在 → 建立預設檔
if not os.path.exists(CONFIG_PATH):
    create_default_config(CONFIG_PATH)

# 讀取設定檔
config = configparser.ConfigParser()
config.read(CONFIG_PATH, encoding="utf-8")

# YOLO
YOLO_MODEL = config.get("YOLO", "MODEL", fallback=DEFAULT_CONFIG["YOLO"]["MODEL"])
YOLO_CONF = config.getfloat("YOLO", "CONF", fallback=float(DEFAULT_CONFIG["YOLO"]["CONF"]))
YOLO_IOU = config.getfloat("YOLO", "IOU", fallback=float(DEFAULT_CONFIG["YOLO"]["IOU"]))
YOLO_IMGSZ = config.getint("YOLO", "IMGSZ", fallback=int(DEFAULT_CONFIG["YOLO"]["IMGSZ"]))

# CAMERA
CAM_INDEX = config.getint("CAMERA", "INDEX", fallback=int(DEFAULT_CONFIG["CAMERA"]["INDEX"]))
# CAM_INDEX = 0
FRAME_W = config.getint("CAMERA", "WIDTH", fallback=int(DEFAULT_CONFIG["CAMERA"]["WIDTH"]))
FRAME_H = config.getint("CAMERA", "HEIGHT", fallback=int(DEFAULT_CONFIG["CAMERA"]["HEIGHT"]))

# HAND
HAND_DRAW = config.getboolean("HAND", "DRAW", fallback=DEFAULT_CONFIG["HAND"]["DRAW"] == "True")

# ALERT
ALERT_COOLDOWN_S = config.getfloat("ALERT", "COOLDOWN_S",
                                   fallback=float(DEFAULT_CONFIG["ALERT"]["COOLDOWN_S"]))

# SERIAL
SERIAL_BAUD = config.getint("SERIAL", "BAUD",
                            fallback=int(DEFAULT_CONFIG["SERIAL"]["BAUD"]))
# ============================================================

# ---- Auto device/precision/tracker selection ----
HAS_CUDA = torch.cuda.is_available()
DEVICE   = 0 if HAS_CUDA else "cpu"
USE_HALF = True if HAS_CUDA else False                 # CPU must be False
TRACKER  = "botsort.yaml" if HAS_CUDA else "bytetrack.yaml"  # CPU uses ByteTrack

def detect_arduino():
    """
    Auto-detect common Arduino-compatible USB VID/PID and open serial.
    Returns: serial.Serial or None
    """
    ARDUINO_IDS = {
        ("2341", "0043"),  # Arduino Uno (genuine)
        ("2341", "0010"),  # Arduino Mega (genuine)
        ("1A86", "7523"),  # CH340/CH341 clones
        ("10C4", "EA60"),  # CP210x
        ("0403", "6001"),  # FT232R
    }
    candidates = []
    for p in list_ports.comports():
        vid = f"{p.vid:04X}" if p.vid is not None else None
        pid = f"{p.pid:04X}" if p.pid is not None else None
        print(f"USB device: vid={vid} pid={pid} desc={p.description}")
        if vid and pid and (vid, pid) in ARDUINO_IDS:
            candidates.append(p)

    for p in candidates:
        try:
            ser = serial.Serial(p.device, SERIAL_BAUD, timeout=0.2)
            time.sleep(2.0)  # allow board reset
            print(f"[Serial] Connected: {p.device}")
            return ser
        except serial.SerialException as e:
            print(f"[Serial] Open failed on {p.device}: {e}")
    print("[Serial] No Arduino connected")
    return None

def send_to_arduino(ser, msg: str):
    """Safe send. Adds newline. Ignores if serial not available."""
    if ser is None or not ser.writable():
        return
    try:
        ser.write((msg + "\n").encode("utf-8"))
    except Exception as e:
        print(f"[Serial] Send error: {e}")

# ---- MediaPipe Hands (fast settings) ----
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=4,
    model_complexity=0,              # fastest
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)
mp_draw = mp.solutions.drawing_utils

# ---- Init YOLO ----
model = YOLO(YOLO_MODEL)

# ---- Camera ----
# cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_DSHOW)
cap = cv2.VideoCapture(CAM_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)
if not cap.isOpened():
    print("Failed to open camera")
    raise SystemExit
cv2.setUseOptimized(True)

# ---- Arduino ----
arduino = detect_arduino()

# ---- Alert state (edge-trigger with cooldown for OFF) ----
alert_on = False
last_safe_t = time.time()

def hand_hulls_from_result(res, W, H):
    """Return list of Nx1x2 hulls (float32) for each hand with >=3 points."""
    hulls = []
    if not res or not res.multi_hand_landmarks:
        return hulls
    for hlm in res.multi_hand_landmarks:
        pts = []
        for lm in hlm.landmark:
            x = int(lm.x * W)
            y = int(lm.y * H)
            pts.append([x, y])
        if len(pts) >= 3:
            pts = np.array(pts, dtype=np.float32).reshape(-1, 2)
            pts = pts[np.isfinite(pts).all(axis=1)]
            if len(pts) >= 3:
                hull = cv2.convexHull(pts).astype(np.float32)
                if hull.ndim == 2:
                    hull = hull.reshape(-1, 1, 2)
                hulls.append(hull)
    return hulls

def rect_poly_from_xyxy(x1, y1, x2, y2):
    poly = np.array([[x1, y1],[x2, y1],[x2, y2],[x1, y2]], dtype=np.float32).reshape(-1,1,2)
    return poly

def yolo_track_safe(model, frame):
    """
    Run model.track with safe fallbacks:
    - Try selected tracker + half
    - If ValueError/ImportError/etc, retry with half=False
    - If still fails on BoT-SORT (e.g., lap missing), fallback to ByteTrack
    """
    # First try with chosen settings
    try:
        return model.track(frame, imgsz=YOLO_IMGSZ, conf=YOLO_CONF, iou=YOLO_IOU,
                           device=DEVICE, half=USE_HALF, verbose=False,
                           tracker=TRACKER, persist=True)
    except Exception as e1:
        # Retry without half
        try:
            return model.track(frame, imgsz=YOLO_IMGSZ, conf=YOLO_CONF, iou=YOLO_IOU,
                               device=DEVICE, half=False, verbose=False,
                               tracker=TRACKER, persist=True)
        except Exception as e2:
            # Fallback to ByteTrack
            try:
                return model.track(frame, imgsz=YOLO_IMGSZ, conf=YOLO_CONF, iou=YOLO_IOU,
                                   device=DEVICE, half=False, verbose=False,
                                   tracker="bytetrack.yaml", persist=True)
            except Exception as e3:
                print(f"[Tracker] Failed: {e3}")
                return []  # no results

prev_t = time.time()
while True:
    ok, frame = cap.read()
    if not ok:
        break
    H, W = frame.shape[:2]

    # ---- Hands ----
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    hand_res = hands.process(rgb)
    hand_hulls = hand_hulls_from_result(hand_res, W, H)

    if HAND_DRAW and hand_res and hand_res.multi_hand_landmarks:
        for hlm in hand_res.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hlm, mp_hands.HAND_CONNECTIONS)

    # ---- YOLO + Tracker (safe) ----
    yolo_res = yolo_track_safe(model, frame)
    any_overlap = False

    for r in yolo_res:
        if r.boxes is None:
            continue
        ids = r.boxes.id  # may be None initially

        for i, b in enumerate(r.boxes):
            x1, y1, x2, y2 = map(int, b.xyxy[0])
            conf = float(b.conf[0]) if b.conf is not None else 0.0
            cls_id = int(b.cls[0]) if b.cls is not None else -1

            tid = None
            if ids is not None and len(ids) > i and ids[i] is not None:
                try:
                    tid = int(ids[i])
                except Exception:
                    tid = None

            rect_poly = rect_poly_from_xyxy(x1, y1, x2, y2)
            overlap = False
            for hull in hand_hulls:
                inter_area, inter_poly = cv2.intersectConvexConvex(hull, rect_poly)
                if inter_area > 0 and inter_poly is not None and len(inter_poly) >= 3:
                    overlap = True
                    # visual: fill intersection red
                    inter_i32 = inter_poly.astype(np.int32)
                    cv2.fillPoly(frame, [inter_i32], (0, 0, 255))
            any_overlap |= overlap

            color = (0, 0, 255) if overlap else (0, 0, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            label = f"Weapon {conf:.2f}"
            if tid is not None:
                label = f"ID {tid} | " + label
            cv2.putText(frame, label, (x1, max(20, y1 - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # ---- Arduino edge-triggered ON/OFF with cooldown ----
    now = time.time()
    if any_overlap:
        last_safe_t = now
        if not alert_on:
            alert_on = True
            send_to_arduino(arduino, "ON")
    else:
        if alert_on and (now - last_safe_t) >= ALERT_COOLDOWN_S:
            alert_on = False
            send_to_arduino(arduino, "OFF")

    # ---- HUD (FPS + state) ----
    fps = 1.0 / max(1e-6, (now - prev_t))
    prev_t = now
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    state_text = "ALERT" if alert_on else "SAFE"
    state_color = (0, 0, 255) if alert_on else (0, 200, 0)
    cv2.putText(frame, f"STATE: {state_text}", (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, state_color, 2)

    cv2.imshow("Danger Detection (YOLO + Tracker + Arduino)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ---- Cleanup ----
try:
    if alert_on:
        send_to_arduino(arduino, "OFF")
except Exception:
    pass

hands.close()
cap.release()
cv2.destroyAllWindows()
if arduino is not None:
    try:
        arduino.close()
    except Exception:
        pass
