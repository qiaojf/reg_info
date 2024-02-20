import os
import json


cls_dict = ['3','4','5','6','7','8','9','10','J','Q','K','A','2','BJ','CJ','PASS']

label_path = './label/'
filespath = './json/'

files = os.listdir(filespath)
for file in files:
    with open(filespath+file,'r',encoding='utf-8') as f:
        content = json.load(f)

    filename = file.split('.')
    with open(label_path+filename[0]+'.txt','w',encoding='utf-8') as f:
        for item in content['shapes']:
            if item['label'] == 'B':
                print(label_path+filename[0]+'.txt')
            try:
                f.write(str(cls_dict.index(item['label']))+' ')
                f.write(str(item['points'][0][0]/1440)+' '+str(item['points'][0][1]/990)+' '+str(item['points'][1][0]/1440)+' '+str(item['points'][1][1]/990)+'\n')
            except ValueError as e:
                print(e)
                continue










