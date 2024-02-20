import socket,sys
import os
import struct
import hashlib
import json

import shutil  
import threading
import time
import hashlib
import pyautogui
import win32api
import win32con
import win32gui
from PIL import Image, ImageGrab
from skimage import io

from get_windows import in_game



players = ['player1','player2','player3']
def get_img():
    i = 1
    while True:
        if win32gui.FindWindow(0, '斗地主角色版'):
            while True:
                img = ImageGrab.grab((120, 0, 1560, 1020))  # x=1440 y=1020
                file = './{}.png'.format(i)
                try:
                    img.save(file)
                except:
                    print('wrong!')
                    img.save(file)
                img = io.imread(file)
                if img[130,800,1] in (64,88): #没有地主牌，
                    pass
                elif img[130,800,1] not in (64,88): # 有地主牌
                    if img[850,100,1] not in (64,88): #and img[440,150,1] not in (64,88): #计时器在当前玩家
                        break
                    elif img[380,150,1] not in (64,88): #and img[450,1290,1] not in (64,88): #计时器在上家
                        break
                    elif img[380,1280,1] not in (64,88): #and img[770,700,1] not in (64,88):   #计时器在下家
                        break
                    elif img[850,100,1] in (64,88) and img[380,150,1] in (64,88) and img[380,1280,1] in (64,88):  # 没有计时器
                        break
            if i == 1:
                io.imsave('./1.png', img)
            else:
                old_img = io.imread('./{}.png'.format(i-1))
                if img[850,100,1]==old_img[850,100,1] and img[380,150,1]==old_img[380,150,1] and img[380,1280,1]==old_img[380,1280,1]:
                    try:
                        os.remove('./{}.png'.format(i-1))
                    except:
                        print('wrong!')
                        os.remove('./{}.png'.format(i-1))
                else:
                    try:
                        os.remove('./{}.png'.format(i-1))
                    except:
                        print('wrong!')
                        os.remove('./{}.png'.format(i-1))
                    io.imsave('./tmp/{}.png'.format(i), img)
            i += 1
        else:
            in_game()
            files = os.listdir('./tmp/')  
            for j in files:
                os.remove('./tmp/{}'.format(j))

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
        if record == []:
            pass
        elif record[-1] == (back_player,back_player_cards):
            record.append((forward_player,forward_player_cards))
        elif record[-1] == (my_player,['PASS']):
            record.append((back_player,back_player_cards))
            record.append((forward_player,forward_player_cards))
    elif forward_player_cards != [] and back_player_cards == [] and my_cards != []: # 下家出牌
        if record == []:
            pass
        elif record[-1] == (forward_player,forward_player_cards):
            record.append((my_player,my_cards))
        elif record[-1] == (back_player,['PASS']):
            record.append((forward_player,forward_player_cards))
            record.append((my_player,my_cards))
    elif forward_player_cards == [] and back_player_cards != [] and my_cards != []: # 上家出牌
        if record == []:
            pass
        elif record[-1] == (my_player,my_cards):
            record.append((back_player,back_player_cards))
        elif record[-1] == (forward_player,['PASS']):
            record.append((my_player,my_cards))
            record.append((back_player,back_player_cards))
    elif forward_player_cards != [] and back_player_cards != [] and my_cards != []:
        if record == []:
            pass
        elif record[-1] == (forward_player,forward_player_cards): #下家出牌
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
    ADDR =('192.168.1.6',9999)
    sock = socket.socket()
    sock.connect(ADDR)
    print('connected success')
    record = []
    player_mark = []
    # try:
    while True:
        pic_path = './tmp/'
        if len(os.listdir(pic_path)) > 1:
            filelist = sorted(os.listdir(pic_path),key=lambda x:int(x[:-4]))
            filepath = pic_path + filelist[0]
            if os.path.isfile(filepath):
                fileinfo_size = struct.calcsize('64sl64s')
                with open(filepath, 'rb') as fp:
                    data = fp.read()
                img_md5 = hashlib.md5(data).hexdigest()
                fhead = struct.pack('64sl64s', bytes(os.path.basename(filepath).encode('utf-8')),os.stat(filepath).st_size,img_md5.encode(encoding='utf-8'))
                sock.send(fhead)
                sock.sendall(data)
                print ('{0} file send over...'.format(filepath))
                res = sock.recv(512).decode()
                if res == 'file send over!':
                    res_size = sock.recv(512).decode()
                    recv_size  = 0   
                    recv_data = b''  
                    while recv_size < int(res_size):  
                        res_data = sock.recv(512)
                        recv_size += len(res_data)  
                        recv_data += res_data
                    os.remove(filepath)
                    recv_data = eval(recv_data)
                    dt_boxes,rec_res = recv_data[0],recv_data[1]
                    forward_player_cards,back_player_cards,my_cards,my_left_cards = deal_data(dt_boxes,rec_res)
                    print('上家：{0},本家：{1},下家：{2}'.format(forward_player_cards,my_cards,back_player_cards))
                    record,player_mark = get_record(player_mark,record,forward_player_cards,back_player_cards,my_cards)
                elif res == 'file send wrong!':
                    continue
    # except Exception:
    #     print('error')
    #     sock.close()
    #     sys.exit()


t1 = threading.Thread(target=get_img, args=())
t2 = threading.Thread(target=socket_client, args=())

t1.start()
t2.start()






