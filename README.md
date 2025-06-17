# MRT-dangerous-object-detection-system(YOLOv11)

本系統為一套可部署於捷運站、接運車廂內、工廠、作業場域的危險物品偵測警報系統，整合 YOLOv11 模型、即時影像辨識、RS232 控制停機、Teams 推播與圖片紀錄等模組，達成事件即時辨識與自動化處置。

---

## 專案結構
```
├── main.py                   # 主控系統程式
├── demo_yolo_cam.py          # 測試攝影機辨識
├── config.ini                # 系統參數設定
├── requirements.txt          # 套件依賴清單
├── classes.txt               # 類別定義（0: knife）
├── utils/
│   ├── notify.py             # Teams & LINE 警報模組
│   └── rs232.py              # RS232 控制模組
├── detect.py / capture.py    # YOLO 推理與影像擷取模組（可整合 main.py）
└── logs/                     # 紀錄辨識結果（圖片與座標）
```
## 系統功能與特色

-YOLOv11 區辨刀械等危險物，支援即時畫面處理

-自動儲存偵測畫面與標註 TXT

-偵測類別可觸發 Teams 通知

-整合 RS232 停機控制指令

-支援 LINE Notify / HTTP API 通知

-自動建立當日紀錄資料夾並分類存檔

## 安裝環境需求

項目	      說明

作業系統   	Windows 10 / Ubuntu 20.04

Python 版本	Python 3.10 以上

GPU 支援   	CUDA 11.7 + NVIDIA RTX 3060↑

套件依賴    	OpenCV、PyTorch、Ultralytics、pygame、requests、pypylon 等

## 安裝與啟動
```
# 建立虛擬環境
python -m venv env
source env/bin/activate   # Linux/macOS
env\Scripts\activate      # Windows

# 安裝套件
pip install -r requirements.txt

# 執行主程式
python main.py
config.ini 

[Factory]
Wo = W00123
Operator = James
Side = Front
Product = Knife

[YoloSetting]
Conf = 0.3
ClassNames = ['knife', 'gun']
ClassAlarms = [0]          # 類別索引
ClassSavePictures = [0]

[RS232]
RS232_stop = True
RS232_COM = COM3

[TeamsNotify]
TeamsNotify = True
Channel = 安全室
```
## 功能說明

模組	                                    功能描述

-Detect_from_img_and_alarm_and_save_img()	模型推理後觸發儲存、標註、Teams 警報、RS232 停機指令

-Read_Config()	                          讀取 config.ini 並初始化系統參數

-send_Teams_notify()	                    發送 JSON 結構 Teams 卡片訊息給指定頻道

-STOP_Label()	                            發送 16 bytes 的停機 RS232 指令至 COM PORT

-line_notify()	                          使用 HTTP API 傳送警報通知

-Create_folder_and_classestxt()	          自動建立資料夾與類別說明檔

## 訓練的環境配置

![image](https://github.com/user-attachments/assets/49292ecd-0719-4378-8f37-1a7f707a227f)

![image](https://github.com/user-attachments/assets/a4a85680-688d-41ea-ae03-d05d0bb6b042)

![image](https://github.com/user-attachments/assets/f370d4f7-7d71-40d0-89a5-0adec8233355)


## 成果預覽（訓練/推論）

![image](https://github.com/user-attachments/assets/ae88c73c-4a34-4778-92cd-ea62e246cbfd)

![image](https://github.com/user-attachments/assets/3d9c6c16-e3c4-4fe9-820a-215ce4056f78)

![image](https://github.com/user-attachments/assets/22999854-7c0f-445e-b4ea-142d088f0505)

![image](https://github.com/user-attachments/assets/d0fe43dd-7d80-4c5a-853c-fe726db47e8a)

![image](https://github.com/user-attachments/assets/9ed919f6-74d0-411a-a98e-b41c8de127e1)

![image](https://github.com/user-attachments/assets/fcd836ee-04d4-4e0b-8760-9aaf1399cabb)

![image](https://github.com/user-attachments/assets/52683c29-313c-4524-964e-020c9f4aef9f)


## 實例截圖
![image](https://github.com/user-attachments/assets/4d2f5b13-ce2c-437b-b9f9-09f514ca2a5d)

![image](https://github.com/user-attachments/assets/1694c2f8-300c-4163-9091-39ddde59c695)

![image](https://github.com/user-attachments/assets/1127461c-d6d6-4505-96ae-d61bd20971d6)

![image](https://github.com/user-attachments/assets/faf5506e-8300-468c-bdb1-43c78bdddc2e)

![image](https://github.com/user-attachments/assets/27ea76a0-0f46-484d-9d99-703e7db12ace)

![image](https://github.com/user-attachments/assets/70b801f6-b532-4c67-9088-cfb81dcf58b0)

![image](https://github.com/user-attachments/assets/69ee5ea2-b4fd-4b55-9a8b-9e4bb45fb1ac)

## 實例影片

https://github.com/user-attachments/assets/ce19ca1e-e3bc-41ba-9c51-e84a63b94d14

https://github.com/user-attachments/assets/2a0fdcb6-c2ef-4011-b429-54e390ead90c

## License
本系統為大學專題開發，授權僅限非商業使用。如需商業應用請與原開發者聯繫取得授權。

## 開發團隊

組長:鄧佳宇

成員:戴育崙、霍世翊、陳瑋澤、蘇逸安、李晟祥、張亦然

所屬單位：淡江大學 資訊管理學系

開發時間：2025 上半年
