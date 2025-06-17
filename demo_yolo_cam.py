from ultralytics import YOLO
import cv2

# 載入 YOLO 模型（best.pt）
model = YOLO('best.pt')

# 開啟相機（編號 0）
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("無法開啟攝影機")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # YOLOv8 偵測 (返回物件框等資訊)
    results = model.predict(frame, verbose=False)

    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            if cls_id == 0:
                # 畫紅框
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                # 顯示"Danger"字樣
                cv2.putText(frame, f"Danger ({conf:.2f})", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    # 顯示畫面
    cv2.imshow("YOLOv8 Detection", frame)

    # 按下 q 鍵離開
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 釋放資源
cap.release()
cv2.destroyAllWindows()