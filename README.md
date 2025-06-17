# MRT-dangerous-object-detection-system(YOLOv11)

本系統為一套可部署於捷運站、接運車廂內、工廠、作業場域的危險物品偵測警報系統，整合 YOLOv11 模型、即時影像辨識、RS232 控制停機、Teams 推播與圖片紀錄等模組，達成事件即時辨識與自動化處置。

---

## 專案結構
```
├── main.py                      # 主控制程式（含模型推理 + 警報觸發
├── config.ini                   # 系統參數設定檔
├── detect.py / capture.py      # 攝影機串流與偵測核心模組
├── utils/
│   └── notify.py                # Teams & LINE 推播模組
│   └── rs232.py                 # RS232 控制模組
├── logs/                        # 紀錄辨識結果的截圖與座標
├── classes.txt                  # 分類類別定義
└── requirements.txt             # 相依套件清單
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

## 成果預覽（訓練/推論）

指標	  結果

mAP@0.5	0.160

Precision	0.65

Recall	0.20

FPS	52

-多場域測試通過，包括模擬捷運站月台、低光源環境

-圖片標註與事件紀錄皆可導出

## 實例截圖
![image](https://github.com/user-attachments/assets/8c8472df-3d92-436f-8639-9cb381cb4e90)
![image](https://github.com/user-attachments/assets/86931f97-b219-430a-9513-a9c2e79a0d08)
![image](https://github.com/user-attachments/assets/abb4f002-416e-4ef1-8318-c3615c0304df)

https://github.com/user-attachments/assets/2a0fdcb6-c2ef-4011-b429-54e390ead90c

## License
本系統為大學專題開發，授權僅限非商業使用。如需商業應用請與原開發者聯繫取得授權。

## 開發團隊

組長:鄧佳宇

成員:戴育崙、霍世翊、陳瑋澤、蘇逸安、李晟祥、張亦然

所屬單位：淡江大學 資訊管理學系

開發時間：2025 上半年
