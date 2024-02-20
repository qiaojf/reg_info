
import json
import os
import socket
import struct
import sys
import threading
import time
import pyautogui
import win32api
import win32con
import win32gui
from PIL import Image, ImageGrab
from skimage import io
import hashlib
# from auto_control import in_game

players = ['player1','player2','player3']
def get_img():
    i = 1
    while True:
        if win32gui.FindWindow(0, '斗地主角色版'):
            while True:
                img = ImageGrab.grab((120, 0, 1560, 1020))  # x=1440 y=1020
                file = './{}.png'.format(i)
                img.save(file)
                img = io.imread(file)
                if img[130,800,1] in (64,88): #没有地主牌，
                    pass
                elif img[130,800,1] not in (64,88): # 有地主牌
                    if img[850,100,1] not in (64,88): #and img[440,150,1] not in (64,88): #计时器在当前玩家
                        # print('本家出牌中...')
                        break
                    elif img[380,150,1] not in (64,88): #and img[450,1290,1] not in (64,88): #计时器在上家
                        # print('上家出牌中...')
                        break
                    elif img[380,1280,1] not in (64,88): #and img[770,700,1] not in (64,88):   #计时器在下家
                        # print('下家出牌中...')
                        break
                    elif img[850,100,1] in (64,88) and img[380,150,1] in (64,88) and img[380,1280,1] in (64,88):  # 没有计时器
                        # print('游戏结束')
                        break
            if i == 1:
                io.imsave('./1.png', img)
            else:
                old_img = io.imread('./{}.png'.format(i-1))
                if img[850,100,1]==old_img[850,100,1] and img[380,150,1]==old_img[380,150,1] and img[380,1280,1]==old_img[380,1280,1]:
                    os.remove('./{}.png'.format(i-1))
                else:
                    os.remove('./{}.png'.format(i-1))
                    io.imsave('./tmp/{}.png'.format(i), img)
            i += 1

def deal_data(dt_boxes,rec_res):
    lord_cards = []
    forward_player_cards = []
    back_player_cards = []
    my_cards = []
    my_left_cards = []
    bbox = sorted(dt_boxes,key=lambda x: x[0],reverse=True)
    for i in bbox:
        if float(i[1]) < 0.1961:  #地主牌
            lord_cards.append(rec_res[dt_boxes.index(i)])
        elif float(i[0]) < 0.4167 and float(i[1]) < 0.58824 and float(i[1]) > 0.3922 and float(i[0]) > 0.083:  #上家出牌
            forward_player_cards.append(rec_res[dt_boxes.index(i)])
        elif float(i[0]) > 0.5556 and float(i[1]) < 0.58824 and float(i[1]) > 0.3922 and float(i[0]) < 0.9097:  #下家出牌
            back_player_cards.append(rec_res[dt_boxes.index(i)])
        elif float(i[1]) > 0.82353:    #当前玩家手牌
            my_left_cards.append(rec_res[dt_boxes.index(i)])
        elif float(i[1]) > 0.58824 and float(i[1]) < 0.82353 and float(i[0]) > 0.083 and float(i[0]) < 0.9097: #当前玩家出牌
            my_cards.append(rec_res[dt_boxes.index(i)])
    return forward_player_cards,back_player_cards,my_cards,my_left_cards

def get_record(player_mark,record,forward_player_cards,back_player_cards,my_cards):
    def get_player():
        if player_mark == []:
            forward_player,my_player,back_player = 'forward_player','my_player','back_player'
        else:
            if player_mark[0] == 'forward_player':
                forward_player,my_player,back_player = players[0],players[1],players[2]
            elif player_mark[0] == 'my_player':
                forward_player,my_player,back_player = players[2],players[0],players[1]
            elif player_mark[0] == 'back_player':
                forward_player,my_player,back_player = players[1],players[2],players[0]
        return forward_player,my_player,back_player
    def game_over():
        game_over = False
        left_num1,left_num2,left_num3=0,0,0
        if record != []:
            records =[x for x in record if x[1]!=['PASS']]
            for i in records:
                if i[0] == players[0]:
                    left_num1 += len(i[1])
                elif i[0] == players[1]:
                    left_num2 += len(i[1])
                elif i[0] == players[2]:
                    left_num3 += len(i[1])
            if left_num1 == 20 or left_num2 == 17 or left_num3 == 17:
                game_over = True
        return game_over
    def write_record(record,player_mark):
        with open('./game_record.txt','a',encoding="utf-8") as f:
            f.write(str(record)+','+'\n')
        record = []
        player_mark = []
        return record,player_mark

    forward_player,my_player,back_player = get_player()
    if forward_player_cards != [] and back_player_cards == [] and my_cards == []: 
        if len(record) == 0:    #上家首先出牌
            player_mark.append(forward_player)
            record.append((players[0],forward_player_cards))
        else:
            if record[-1] == (my_player,['PASS']):
                record.append((back_player,['PASS']))
                record.append((forward_player,forward_player_cards))
            elif record[-1] == (back_player,['PASS']):
                record.append((forward_player,forward_player_cards))
    elif forward_player_cards == [] and back_player_cards != [] and my_cards == []: 
        if len(record) == 0:    #下家首先出牌
            player_mark.append(back_player)
            record.append((players[0],back_player_cards))
        else:
            if record[-1] == (forward_player,['PASS']):
                record.append((my_player,['PASS']))
                record.append((back_player,back_player_cards))
            elif record[-1] == (my_player,['PASS']):
                record.append((back_player,back_player_cards))
    elif forward_player_cards == [] and back_player_cards == [] and my_cards != []: 
        if len(record) == 0:    #当前玩家首先出牌
            player_mark.append(my_player)
            record.append((players[0],my_cards))
        else:
            if record[-1] == (back_player,['PASS']):
                record.append((forward_player,['PASS']))
                record.append((my_player,my_cards))
            elif record[-1] == (forward_player,['PASS']):
                record.append((my_player,my_cards))
    elif forward_player_cards != [] and back_player_cards != [] and my_cards == []: # 当前玩家出牌
        if record[-1] == (back_player,back_player_cards):
            record.append((forward_player,forward_player_cards))
        elif record[-1] == (my_player,['PASS']):
            record.append((back_player,back_player_cards))
            record.append((forward_player,forward_player_cards))
    elif forward_player_cards != [] and back_player_cards == [] and my_cards != []: # 下家出牌
        if record[-1] == (forward_player,forward_player_cards):
            record.append((my_player,my_cards))
        elif record[-1] == (back_player,['PASS']):
            record.append((forward_player,forward_player_cards))
            record.append((my_player,my_cards))
    elif forward_player_cards == [] and back_player_cards != [] and my_cards != []: # 上家出牌
        if record[-1] == (my_player,my_cards):
            record.append((back_player,back_player_cards))
        elif record[-1] == (forward_player,['PASS']):
            record.append((my_player,my_cards))
            record.append((back_player,back_player_cards))
    elif forward_player_cards != [] and back_player_cards != [] and my_cards != []:
        if record[-1] == (forward_player,forward_player_cards): #下家出牌
            record.append((my_player,my_cards))
        elif record[-1] == (my_player,my_cards): #上家出牌
            record.append((back_player,back_player_cards))
        elif record[-1] == (back_player,back_player_cards): #当前玩家出牌
            record.append((forward_player,forward_player_cards))
    elif forward_player_cards == [] and back_player_cards == [] and my_cards == []:
        record,player_mark = [],[]
    if game_over():
        record,player_mark = write_record(record,player_mark)
 
    return record,player_mark

def socket_client():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('192.168.1.6',9999))
    except socket.error as msg:
        print(msg)
        sys.exit(1)

    record = []
    player_mark = []
    while True:
        pic_path = './tmp/'
        if len(os.listdir(pic_path)) > 1:
            filelist = sorted(os.listdir(pic_path),key=lambda x:int(x[:-4]))
            # print(filelist)
            filepath = pic_path + filelist[0]
            if os.path.isfile(filepath):
                # 定义定义文件信息。128s表示文件名为128bytes长，l表示一个int或log文件类型，在此为文件大小
                fileinfo_size = struct.calcsize('128sl')
                # 定义文件头信息，包含文件名和文件大小
                fhead = struct.pack('128sl', bytes(os.path.basename(filepath).encode('utf-8')),os.stat(filepath).st_size)
                s.send(fhead)
                fp = open(filepath, 'rb')
                data = fp.read()
                s.sendall(data)
                fp.close()
                code = hashlib.md5(data).hexdigest()
                print(code)
                # while True:
                #     data = fp.read(1024)
                #     if not data:
                print ('{0} file send over...'.format(filepath))
                #         fp.close()
                #         break
                #     s.send(data)
                # server_reply = s.recv(2048).decode()
                os.remove(filepath)
                # recv_data = eval(server_reply)
                # dt_boxes,rec_res = recv_data[0],recv_data[1]
                # forward_player_cards,back_player_cards,my_cards,my_left_cards = deal_data(dt_boxes,rec_res)
                # print(forward_player_cards,back_player_cards,my_cards)
                # record,player_mark = get_record(player_mark,record,forward_player_cards,back_player_cards,my_cards)    

def in_game():
    def get_window_pos(name):
        name = name
        handle = win32gui.FindWindow(0, name)
    # 获取窗口句柄
        if handle == 0:
            return None
        else:
            return win32gui.GetWindowRect(handle), handle

    #获取QQ游戏句柄
    (x1, y1, x2, y2), handle1 = get_window_pos('QQ游戏')
    win1 = win32gui.SetForegroundWindow(handle1)
    pyautogui.click(150, 150,clicks = 1, button ='left', interval = 0.0)
    time.sleep(1)

    #点击斗地主，进入大厅
    (x1, y1, x2, y2), handle2 = get_window_pos('斗地主')
    win2 = win32gui.SetForegroundWindow(handle2)
    #选择场次
    pyautogui.click(50, 425,clicks = 1, button ='left', interval = 0.0)
    time.sleep(1)
    #选择房间
    pyautogui.click(50, 760,clicks = 1, button ='left', interval = 0.0)
    time.sleep(1)

    while True:
        time.sleep(5)
        if not win32gui.FindWindow(0, '斗地主角色版'):
            pyautogui.press('enter')

            #对桌子进行截图
            img = ImageGrab.grab((x1, y1, x2, y2))  
            file = r"{}.png".format(1)
            img.save(file)

            #判断桌子状态，进入符合条件的
            img = io.imread(file)
            j = 75
            for i in range(10):
                pyautogui.click(j-30, 210,clicks = 1, button ='left', interval = 0.0)
                time.sleep(0.5)
                pyautogui.press('enter')
                j += 160
        else:
            (x1, y1, x2, y2), handle3 = get_window_pos('斗地主角色版')
            win1 = win32gui.SetForegroundWindow(handle3)



t1 = threading.Thread(target=get_img, args=())
t2 = threading.Thread(target=socket_client, args=())
# t3 = threading.Thread(target=in_game, args=())
# t1.start()
t2.start()
# t3.start()





















































