#    ╔═════════╗
#    ║ LIBRARY ║
#    ╚═════════╝
import os
import re
import cv2
import json
import math
import time
import queue
import shutil
import serial
import pygame
import requests
import threading
import ultralytics
import configparser
import urllib.request
import multiprocessing   
from   pypylon     import pylon
from   ultralytics import YOLO
multiprocessing.freeze_support()

#    ╔══════════╗
#    ║ FUNCTION ║
#    ╚══════════╝
# 讀取config檔
def Read_Config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    # [Factory]
    global Wo # 製令
    Wo = config['Factory']['Wo']
    global Operator # 作業員
    Operator = config['Factory']['Operator']
    global Side # 作業面別
    Side = config['Factory']['Side']
    global Product # 產品類型
    Product = config['Factory']['Product']
    # [YoloSetting]
    global Conf # 信心度閾值
    Conf = config['YoloSetting']['Conf']
    global ClassNames # 標籤名稱
    ClassNames = config['YoloSetting']['ClassNames']
    global ClassAlarms # 警報類別
    ClassAlarms = config['YoloSetting']['ClassAlarms']
    global ClassSavePictures # 存照片類別
    ClassSavePictures = config['YoloSetting']['ClassSavePictures']
    # [RS232]
    global RS232_stop # 決定要不要停機
    RS232_stop = config['RS232']['RS232_stop']
    global RS232_COM # 停機線材在電腦的哪一個port
    RS232_COM = config['RS232']['RS232_COM']
    # [TeamsNotify]
    global TeamsNotify # 要不要發Teams Notify
    TeamsNotify = config['TeamsNotify']['TeamsNotify']
    global Channel # TeamsNotify頻道
    Channel = config['TeamsNotify']['Channel']
    
    print(f"製令:{Wo} 作業員:{Operator} 作業面別:{Side} 產品別:{Product}")
    print(f"信心度閾值:{Conf} 類別名稱:{ClassNames} 警報類別:{ClassAlarms} 存圖類別:{ClassSavePictures}")
    print(f"要不要停機:{RS232_stop} 停機線材在電腦的哪一個port:{RS232_COM}")
    print(f"要不要發Teams Notify:{TeamsNotify} TeamsNotify頻道:{Channel}")

def GET_COM():
    # global rs232_stop
    mBuandBit = 38400
    mDataBit = serial.EIGHTBITS
    mStopBit = serial.STOPBITS_ONE
    mParityBit = serial.PARITY_ODD

    try:
        Rs232 = serial.Serial(
            port=RS232_COM,
            baudrate=mBuandBit,
            bytesize=mDataBit,
            parity=mParityBit,
            stopbits=mStopBit,
            timeout=1
        )

        if Rs232.is_open:
            print(f"{RS232_COM} - 打開成功！")
            global send_enabled
            send_enabled = True
            global timer_interval
            timer_interval = 0.1  # Timer interval in seconds
            return Rs232, send_enabled, timer_interval
        else:
            print(f"{RS232_COM} - 打開失敗（通訊端口已打開）~~")
            return None, False, None
    except Exception as ex:
        print(f"Error: {ex}")
        return None, False, None

def STOP_Label():
    global send_enabled
    if Rs232 and send_enabled:
        bDataOut = bytearray([0x25, 0x30, 0x31, 0x23, 0x57, 0x43, 0x53, 0x52, 0x30, 0x30, 0x31, 0x35, 0x31, 0x2A, 0x2A, 0x0D])
        try:
            txtSend = "&H25, &H30, &H31, &H23, &H57, &H43, &H53, &H52, &H30, &H30, &H31, &H35, &H31, &H2A, &H2A, &H0D"
            print(f"Sending: {txtSend}")
            Rs232.write(bDataOut)
        except Exception as ex:
            print(f"Error: {ex}")
        time.sleep(timer_interval)
        # Rs232.close()

# 載入警報音檔
def Load_mp3(mp3_path):
    pygame.mixer.init()
    pygame.mixer.music.load(mp3_path)

# 建立當前製令的資料夾與類別檔
def Create_folder_and_classestxt():
    try:
        os.makedirs(os.path.join(log_path), exist_ok=True)
    except Exception:
        pass
    
    with open(os.path.join(log_path,"classes.txt"), 'a') as file:
        fuck_i=0
        for fuck in ClassNames:
            file.write(str(fuck_i))
            fuck_i = fuck_i+1
            file.write('\n')

# # 指定USB相機與解析度
# def Assign_camera():
#     # start webcam
#     cap = cv2.VideoCapture("http://127.0.0.1:5000/video_feed")
#     # 設定攝像頭參數
#     # width = 1280  # 設定寬度為1280像素
#     # height = 720  # 設定高度為720像素
#     # 設定攝像頭的解析度
#     # cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
#     # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
#     return cap

# 存照片
def save_img(path,img):
    cv2.imwrite(path, img)

# 存座標  
def save_txt(path,text):
    with open(path, 'w',encoding='utf-8') as file:
        file.write(text+'\n')
    file.close()

# 發送Line警報
def line_notify(server_ip):
    try:
        # server_ip = '172.16.170.122'  # Server IP 地址
        server_port = '49152'
        # 發送HTTP請求
        url = f'http://{server_ip}:{server_port}/send_notification'
        urllib.request.urlopen(url)
        
    except Exception:
        print("連線到筆電，發送Notify異常")

# 發送Teams警報
def send_Teams_notify(Channel,Texttttt):
    json_data = {
        "FROM": "YL00212",
        "TO":Channel,
        "System": "貼標機警報",
        "CardContent": {
        },
        "TextContent": Texttttt,
        "Card": False
    }

    # 將 JSON 資料轉換為字串
    json_data = json.dumps(json_data)

    # webhook URL (僅包含基礎路徑)
    webhook_url = "https://ec1web.innodisk.com:3978/EC1Bot/api/NOTICE/Message/Channel"

    # 設定請求頭
    headers = {'Content-Type': 'application/json'}

    # 發送 POST 請求
    response = requests.post(webhook_url, headers=headers, data=json_data)

    # 檢查回應
    if response.status_code == 200:
        print("成功執行TeamsNotify請求")
        print(response.text)
    else:
        print("沒有成功執行TeamsNotify請求")
        print(response.text)
        
# Yolo V8偵測
def Detect_from_img_and_alarm_and_save_img(img):
    global i, confidence
    img_draw = img.copy()
    results = model(img, stream=True, iou=0.8, conf=Conf, verbose=False)
    already_save_picture=False # 讀入新的影像，不可能存過照片
    file_name_rand=str(int(time.time()*100000000))
    file_name_txt = file_name_rand+'.txt'
    file_name_jpg= file_name_rand+'.jpg'

    for r in results:
        boxes = r.boxes
        
        for box in boxes:
            # 獲得當前類別ID 0 1 2 3...
            class_set = int(box.cls[0])
            
            # bounding box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # convert to int values
            
            # 若是觸碰到邊界框，則不辨識
            height, width, channels = img_draw.shape
            skip_pixel = 30
            skip_pixel_ = skip_pixel
            while skip_pixel_>0:# 在圖片上畫線，標記出邊界位置(大藍框)
                cv2.line(img_draw, (skip_pixel_, skip_pixel_), (width-skip_pixel_, skip_pixel_), (255, 0, 0), 1)
                cv2.line(img_draw, (skip_pixel_, skip_pixel_), (skip_pixel_,height-skip_pixel_), (255, 0, 0), 1)
                cv2.line(img_draw, (width-skip_pixel_, height-skip_pixel_), (skip_pixel_, height-skip_pixel_), (255, 0, 0), 1)
                cv2.line(img_draw, (width-skip_pixel_, height-skip_pixel_), (width-skip_pixel_,skip_pixel_), (255, 0, 0), 1)
                skip_pixel_=skip_pixel_-4
            if (x1<skip_pixel):
                cv2.circle(img_draw, (x1,y1), 2, (0, 255, 255), 3)
                print(f"框框碰到邊界(左)，觸發忽略，距離:{x1}")
                continue
            elif ((width-x2)<skip_pixel):
                cv2.circle(img_draw, (x2,y2), 2, (173, 216, 230), 3)
                print(f"框框碰到邊界(右)，觸發忽略，距離:{width-x2}")
                continue
            if (y1<skip_pixel):# (汐止廠的是上下)
                cv2.circle(img_draw, (x1,y1), 2, (0, 255, 255), 3)
                print(f"框框碰到邊界(上)，觸發忽略，距離:{y1}")
                continue
            elif ((height-y2)<skip_pixel):
                cv2.circle(img_draw, (x2,y2), 2, (173, 216, 230), 3)
                print(f"框框碰到邊界(下)，觸發忽略，距離:{height-y2}")
                continue

            # confidence
            confidence = math.ceil((box.conf[0]*100))/100
            # print("Confidence --->",confidence)
            # print("Class name -->", ClassNames[class_set])

            # object details
            org = [x1, y1-5]
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 1
            thickness = 2

            # 撥放警報音效
            if class_set in ClassAlarms:
                # trigger_alert()
                if pygame.mixer.music.get_busy():
                    #警報中，不重複警報
                    pass
                else:
                    pygame.mixer.music.play()
            # 觸發警報
            # trigger_alert()
            
            # 存1張照片
            if class_set in ClassSavePictures:
                yolo_x = (x1+x2)/(2*img.shape[1])
                yolo_y = (y1+y2)/(2*img.shape[0])
                yolo_w = (x2-x1)/(img.shape[1])
                yolo_h = (y2-y1)/(img.shape[0])
                
                if not already_save_picture:
                    # 存log照片
                    threads.append(threading.Thread(target = save_img(os.path.join(log_path, file_name_jpg), img), args = (i,)))
                    threads[i].start()
                    i=i+1

                    # Flag 避免1個框 存1次照片
                    already_save_picture = True
                
                # 存座標檔，注意喔!!! 這邊1次只會存1個框，1張照片可能要存幾十次座標
                with open(os.path.join(log_path, file_name_txt), 'a') as file:
                    file.write(str(class_set) + ' ' + str(yolo_x) + ' '+ str(yolo_y) + ' '+ str(yolo_w) + ' ' + str(yolo_h))
                    file.write('\n')

                # 發送Teams警報(沒多線 會很卡)
                if TeamsNotify:
                    threads.append(threading.Thread(target = send_Teams_notify(Channel,f"<br>製令：{Wo}<br>產品：{Product}<br>面別：{Side}<br>警報ID：{class_set}<br>作業人員：{Operator}<br>信心度:{confidence}"), args = (i,)))
                    threads[i].start()
                    i=i+1
                
    
            # 最後才可以畫框、標籤，否則汙染照片
            if class_set in ClassAlarms:
                color = (0, 0, 255)# Fail 顏色
                
                if RS232_stop:
                    # 執行停機(沒多線 會很卡)
                    # threads.append(threading.Thread(target = STOP_Label(), args = (i,)))
                    # threads[i].start()
                    # i=i+1
                    threading.Thread(target=STOP_Label)
                
                
            else:
                color               