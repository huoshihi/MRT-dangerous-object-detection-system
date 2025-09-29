# Sentinel 危險偵測防護(YOLOv12)

Sentinel 是一套專為公共場域與工業環境設計的 危險物品即時偵測系統，可部署於捷運站、接運車廂、工廠、作業場域等多種場景。  
系統核心結合 YOLOv12 物件偵測模型與 MediaPipe 手部關節追蹤套件，能即時分析攝影機影像，判斷使用者是否持握危險物品。  

透過 Arduino 控制 LED 指示燈與馬達鎖，當系統偵測到潛在危險時，會立即發出視覺警示並啟動防護措施，降低事故發生風險。   

Sentinel 不僅提供即時偵測與防護功能，還強調人機協同、資料追蹤與環境安全管理，是一套完整且可落地的智能安全防護解決方案。

---

## 專案結構
```
├── shark_v2.py               # 主控系統程式，整合攝影機辨識、YOLO 推理與影像擷取模組及Arduino程式碼
├── best.pt                   # YOLO 訓練後的權重檔，用於載入模型進行物件偵測推論
├── config.ini                # 系統參數與環境設定         
├── logs/                     # 紀錄辨識結果（圖片與座標）  
└── hardware_control/         # Led燈與馬達鎖                 
```
## 系統功能與特色

- **YOLOv12 即時偵測**：可區辨刀械等危險物，支援即時畫面處理  
- **MediaPipe 輔助**：結合手部關節辨識，降低誤判率  
- **事件記錄**：自動儲存偵測畫面與標註 TXT 檔案  
- **硬體延伸**：透過 Arduino 板子進行實務應用  
- **視覺警示**：LED 燈發光提示危險事件  
- **人機協同**：監控人員在 5 秒內二次確認，避免誤判  
- **安全聯動**：馬達鎖轉開，允許取出櫃子內防身物品   

---

## 系統比較表

| 比較項目     | 傳統監控（人力）        | 單純 AI 偵測             | Sentinel（本研究）                      |
|--------------|-------------------------|--------------------------|----------------------------------------|
| 即時性       | 低（人眼輪巡）          | 高                       | 高                                      |
| 誤報控制     | 依人員經驗              | 受環境影響大             | MediaPipe + 門檻分級，誤警較低          |
| 人機協同     | 無                      | 弱                       | 五秒人工互鎖                            |
| 硬體聯動     | 無                      | 可能（風險高）           | Arduino 安全箱（授權後）                |
| 部署成本/難度 | 低                      | 中                       | 中（需 GPU + 硬體）                     |

---

## 系統環境與依賴

| 項目         | 說明                                                       |
|--------------|------------------------------------------------------------|
| 作業系統     | Windows 10 / Ubuntu 20.04                                   |
| Python 版本  | Python 3.10 以上                                           |
| GPU 支援     | CUDA 11.7 + NVIDIA RTX 3060↑                                |
| 套件依賴     | opencv-python、torch、ultralytics、MediaPipe、numpy 及 pyserial |
| Arduino      | Arduino Uno / Mega 或相容開發板，透過 USB 串列埠通訊控制 LED 與馬達鎖 |  

---
## 安裝與啟動
```
# 安裝 YOLO 目標偵測框架（YOLOv12）
pip install ultralytics

# 安裝 pySerial，用於與 Arduino 進行序列埠通訊
pip install pyserial

# 安裝 MediaPipe，用於手部關鍵點偵測與追蹤       
pip install mediapipe

# 安裝 NumPy，用於數值運算與矩陣處理    
pip install numpy

# 安裝 OpenCV，用於影像擷取、處理與繪圖          
pip install opencv-python

# 安裝 PyTorch，用於深度學習模型推論與 GPU 加速
pip install torch
```
---
## 功能說明


| 模組               | 屬性                                                                 | 方法                                                                                     | 功能描述                                                         |
|--------------------|----------------------------------------------------------------------|--------------------------------------------------------------------------------------------|------------------------------------------------------------------|
| **CameraHandler**     | `source`：攝影機來源<br>`frame`：目前擷取影像                                | `capture()`：擷取即時影像<br>`preprocess()`：縮放、標準化等預處理                              | 負責與攝影機互動、擷取畫面並進行前處理                              |
| **YOLODetector**       | `model`：YOLOv12 模型<br>`threshold`：偵測門檻值                           | `detect(frame)`：回傳偵測到的物件與座標                                                       | 使用 YOLOv12 模型進行物件偵測                                     |
| **HandAnalyzer**       | `mediapipe_model`：Mediapipe 手部模型                                     | `analyze(frame)`：偵測手部關節<br>`check_interaction(object, hand)`：判斷是否持握危險物品           | 透過 Mediapipe 偵測手部並判斷是否握持危險物                         |
| **RiskEvaluator**      | `risk_level`：低 / 中 / 高                                                  | `evaluate(object, hand)`：依偵測結果判斷風險<br>`debounce()`：防抖處理<br>`cooldown()`：冷卻處理     | 綜合物件與手部資訊評估當前風險等級                                 |
| **ArduinoController**  | `port`：連接埠<br>`status`：目前狀態（READY、ARMING、BUTTON_PRESS、OPENING、TIMEOUT、ERROR） | `send_command(cmd)`：傳送指令<br>`receive_response()`：接收回報<br>`unlock_box()`：解鎖安全箱         | 負責與 Arduino 通訊，控制 LED 與馬達鎖                              |
| **EventLogger**         | `event_id`：事件編號<br>`timestamp`：時間戳記<br>`data`：影像與狀態資訊         | `save_event()`：存檔事件<br>`export_log()`：輸出報告                                              | 紀錄每次偵測事件，保存影像與資訊以利後續分析|

---
## 訓練的環境配置

![image](https://github.com/user-attachments/assets/49292ecd-0719-4378-8f37-1a7f707a227f)

![image](https://github.com/user-attachments/assets/a4a85680-688d-41ea-ae03-d05d0bb6b042)

![image](https://github.com/user-attachments/assets/f370d4f7-7d71-40d0-89a5-0adec8233355)

---
## ARDUINO連接演示與實作示範

![image](https://github.com/user-attachments/assets/761f7909-81ae-4544-a80a-d9d58cd64123)

![image](https://github.com/user-attachments/assets/7d2bea5e-375a-49f2-9dbe-c2ad04026855)  

![ad1](https://github.com/user-attachments/assets/8b6b8e75-f150-4abb-9476-15852880248b)

![ad207280-f9e7-4816-b26d-3daaaca06933](https://github.com/user-attachments/assets/b7d34c2f-db5d-49f2-80de-cec69e792285)

![ef45a292-412d-4d39-ad03-c0ddd5d7f316](https://github.com/user-attachments/assets/318a3584-f7ea-46c0-bccc-ab43422eb3ea)

![550e1643-38c9-4e36-9934-58b733430815](https://github.com/user-attachments/assets/be30b35c-715d-4de8-8ba0-f315f69c090b)

![S__46923782](https://github.com/user-attachments/assets/24b69ea8-f22e-430d-8f85-8f7dbbe1c621)  

---
## 成果預覽（訓練/推論）

<img width="814" height="543" alt="image" src="https://github.com/user-attachments/assets/97bd15ac-8018-4218-b749-42026541499e" />  

precision 和 recall 大多能維持在 0.9 以上，整體 mAP@0.5 約 0.917

<img width="826" height="551" alt="image" src="https://github.com/user-attachments/assets/de32151a-ada6-487a-9a9a-8729dfdfea5d" />  

confidence ≈ 0.4 時，recall 大約能維持在 0.93，代表此區間可以兼顧較高的召回率

<img width="891" height="445" alt="image" src="https://github.com/user-attachments/assets/146a5e4a-008d-4adf-8b03-8def62c0616c" />  

在訓練過程中，分類相關的 cls_loss 收斂非常穩定，顯示模型在類別判斷上的學習效果相當出色。雖然 box_loss 與 dfl_loss 下降速度相對較慢，說明邊框定位的精度與品質仍有進步空間，但整體趨勢持續改善。驗證集的表現與訓練集一致，沒有明顯過擬合現象，這顯示模型具有良好的泛化能力。性能指標方面，模型 precision 與 recall 均達 0.88~0.89，mAP@0.5 高達 0.92，表明在一般 IOU 門檻下，模型的偵測與分類效果非常優異；而 mAP@0.5:0.95 約 0.59，提示在較嚴格的邊框要求下仍有提升空間。整體而言，模型在核心任務上的表現已經相當不錯。

<img width="854" height="640" alt="image" src="https://github.com/user-attachments/assets/11596c12-b493-4659-b079-10547f029a78" />  

從混淆矩陣分析可知，模型在測試資料中 正確檢出的數量（TP）為 1111，誤將背景判為目標（FP）為 121，以及 未檢出的數量（FN）為 101，整體混淆率約 8%，屬於可接受範圍。換算後，precision 約 0.90，recall 約 0.92，與前述 PR 曲線結果一致。從歸一化混淆矩陣可見，模型對正樣本辨識率高達 0.92，對背景的判斷幾乎為 1.0，顯示模型在 背景過濾 上表現非常出色。雖然整體表現優異，但在 降低誤報（FP）方面仍有改善空間，可透過調整 confidence 門檻或強化負樣本訓練來進一步優化。

<img width="875" height="583" alt="image" src="https://github.com/user-attachments/assets/221cba35-d811-4ddc-a8ab-3099eebfcf41" />  

從 F1 分數分析可知，當 confidence 門檻約 0.42 時，模型的 F1 分數達到最佳值約 0.90，表示在此門檻下 precision 與 recall 取得了良好的平衡，模型在偵測準確性與完整性上表現相當穩定。  


<img width="846" height="846" alt="image" src="https://github.com/user-attachments/assets/20de87f0-ec97-4ac0-b81f-f77862545fd8" />  

![8000](https://github.com/user-attachments/assets/f236488e-006a-4c9b-8575-9f2ddddf1f27)

這兩張圖展示了專題資料集的分布情況。資料集中約有 8000 筆樣本，但目標物的寬度與高度大多小於影像比例的 0.2，換言之，絕大部分為小物件。這種分布會導致模型在 mAP@0.5:0.95 指標下表現較低，因為高 IoU 標準下，小物件邊界容易受到誤差影響。此外，標註位置大多集中於畫面中間，顯示資料拍攝角度或場景具有一定一致性。整體而言，資料能有效訓練模型辨識目標，但若想提升定位精準度，仍需補充更多小物件、多角度與多樣化場景的樣本，以增強模型在不同情境下的泛化能力。

<img width="891" height="594" alt="image" src="https://github.com/user-attachments/assets/005140b9-4702-40f1-ba5d-ecad30b036b5" />  

從圖中可以看出，confidence 門檻越高，precision 越高，在 0.92 以上時，precision 幾乎達到 100%，代表誤報幾乎沒有。然而，高門檻會導致 recall 急速下降，增加漏檢風險。實務上，若希望平衡 precision 與 recall，會建議將門檻設在 0.4~0.5。

---
## 實例截圖

**資料集卷軸演示**  

<img width="679" height="679" alt="image" src="https://github.com/user-attachments/assets/d4bad218-d56d-486c-bfae-e20244a3a9bf" />

<img width="679" height="679" alt="image" src="https://github.com/user-attachments/assets/0232e565-ea9b-4e64-b6a5-a21002dd8328" />

<img width="790" height="453" alt="image" src="https://github.com/user-attachments/assets/63e1aba7-97d3-4646-b3c9-f1ae94e128f2" />

<img width="773" height="773" alt="image" src="https://github.com/user-attachments/assets/c15fe0b2-f1f8-44de-9421-491bac595d1e" />  

**程式運行報警演示**

![alert1](https://github.com/user-attachments/assets/d5f4ec2e-d561-4a12-aff6-a300e1058e98)  

![alert2](https://github.com/user-attachments/assets/849e82f7-3b0f-4184-bc57-8603ddf37ac5)

---
## 測試示範影片

本測試示範影片使用以下規格作為演示：  

| 項目       | 規格                                   |
|------------|----------------------------------------|
| **攝影機** | DroidCam 連接 黑鯊 2 手機              |
| **微控制器** | Arduino Mega 2560 R3 (副廠)           |
| **執行模組** | Tower Pro SG90 馬達                   |
| **主機 CPU** | Intel Core i7-11800H                  |
| **主機 GPU** | NVIDIA RTX 3050 Ti (4GB VRAM)         |
| **記憶體** | 16GB DDR4                              |
| **作業系統** | Windows 11                            |


https://github.com/user-attachments/assets/c10798b5-5038-4603-8ccb-07cfc4302f7c

https://github.com/user-attachments/assets/dc5cc813-33e6-49e6-8efd-240573a6620b

---

## License  

本系統為大學專題開發，授權僅限非商業使用。如需商業應用請與原開發者聯繫取得授權。

---
## 開發團隊

- **組長**：鄧佳宇  
- **成員**：戴育崙、霍世翊、陳瑋澤、蘇逸安、李晟祥 
- **所屬單位**：淡江大學 資訊管理學系  
- **開發時間**：2025 上半年

---
