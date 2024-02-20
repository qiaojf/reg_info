
import time

import matplotlib.pyplot as plt
import pyautogui
import win32api
import win32con
import win32gui
from PIL import Image, ImageGrab
from skimage import io


def in_game():
    def get_window_pos(name):
        name = name
        handle = win32gui.FindWindow(0, name)
    # 获取窗口句柄
        if handle == 0:
            return None
        else:
            return win32gui.GetWindowRect(handle), handle

    def show_img(name):
        file = './{}.png'.format(name)
        img = Image.open(file)
        plt.imshow(img)
        plt.show()

    def get_pic(name):
        (x1, y1, x2, y2), handle = get_window_pos(name)
        win = win32gui.SetForegroundWindow(handle)
        pyautogui.press('down')
        img = ImageGrab.grab((x1, y1, x2, y2))  
        file = r"{}.png".format(name)
        img.save(file)

    while True:
        if not win32gui.FindWindow(0, 'QQ游戏'):            #没有QQ游戏窗口
            print('请先登录QQ游戏')
            # break
        else:
            if not win32gui.FindWindow(0, '斗地主'):            #没有斗地主窗口
                #获取QQ游戏句柄
                (x1, y1, x2, y2), handle1 = get_window_pos('QQ游戏')
                win1 = win32gui.SetForegroundWindow(handle1)
                pyautogui.press('enter')
                time.sleep(1)
                #点击斗地主，进入大厅
                pyautogui.click(150, 150,clicks = 1, button ='left', interval = 0.0)
                time.sleep(2)
            else:
                if not win32gui.FindWindow(0, '斗地主角色版'):      #没有斗地主角色版窗口
                    (x1, y1, x2, y2), handle2 = get_window_pos('斗地主')
                    win2 = win32gui.SetForegroundWindow(handle2)
                    pyautogui.press('down')
                    time.sleep(1)
                    get_pic('斗地主')
                    img = io.imread('斗地主.png')
                    if img[100,100,0]!=255 and img[100,100,1]!=255 and img[100,100,2]!=255:     #在房间
                        if img[210,75,0]==5 and img[210,75,1]==67 and img[210,75,2]==108:       #关闭万人房
                            pyautogui.click(265, 111,clicks = 1, button ='left', interval = 0.0)
                        else:
                            get_pic('斗地主')
                            img = io.imread('斗地主.png')
                            k = 75
                            for i in range(10):
                                if not win32gui.FindWindow(0, '斗地主角色版'):
                                    if img[210,k,0]!=img[210,k,1]!=img[210,k,2]:
                                        pyautogui.click(k-30, 210,clicks = 1, button ='left', interval = 0.0)
                                        time.sleep(3)
                                    else:
                                        k += 160
                                        i += 1
                                else:
                                    break
                    if img[300,235,0]==204 and img[300,235,1]==204 and img[300,235,2]==204:     # 牌王场已经展开
                        #进入房间
                        pyautogui.click(50, 760,clicks = 1, button ='left', interval = 0.0)
                        time.sleep(2)
                        img = get_pic('斗地主')
                        img = io.imread('斗地主.png')
                        k = 75
                        for i in range(10):
                            if not win32gui.FindWindow(0, '斗地主角色版'):
                                if img[210,k,0]!=img[210,k,1]!=img[210,k,2]:
                                    pyautogui.click(k-30, 210,clicks = 1, button ='left', interval = 0.0)
                                    time.sleep(3)
                                else:
                                    k += 160
                                    i += 1
                            else:
                                break
                    else:#点击牌王场
                        pyautogui.click(50, 425,clicks = 1, button ='left', interval = 0.0)
                        time.sleep(2)
                        pyautogui.press('down')
                else:
                    (x1, y1, x2, y2), handle3 = get_window_pos('斗地主角色版')
                    win3 = win32gui.SetForegroundWindow(handle3)
                    pyautogui.press('enter')
                    break

                


# in_game()



















