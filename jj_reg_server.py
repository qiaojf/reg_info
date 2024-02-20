from socketserver import BaseRequestHandler,ThreadingTCPServer
import threading
import struct
import os
import hashlib
import socket
import sys
import time

from PIL import Image, ImageGrab
from skimage import io

import argparse

import shutil

from pathlib import Path

import cv2
import torch
import torch.backends.cudnn as cudnn
from numpy import random

from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import (
    check_img_size, non_max_suppression, apply_classifier, scale_coords,
    xyxy2xywh, plot_one_box, strip_optimizer, set_logging)
from utils.torch_utils import select_device, load_classifier, time_synchronized

class Handler(BaseRequestHandler):
    def handle(self):
        dirpath = './tmp/'.encode('utf-8')
        address,pid = self.client_address
        print('%s connected!'%address)
        dirpath = ('./tmp/%s/' %address).encode('utf-8')
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        while True:
            fileinfo_size = struct.calcsize('64sl64s')
            buf = self.request.recv(fileinfo_size)
            if buf:
                filename, filesize, img_md5 = struct.unpack('64sl64s', buf)
                fn = filename.strip(str.encode('\00'))
                img_md5 = img_md5.strip(str.encode('\00')).decode()
                new_filename = os.path.join(dirpath, str.encode('new_') + fn)
                with open(new_filename, 'wb') as fp:
                    recvd_size = 0
                    recv_data = b''
                    while recvd_size < int(filesize):
                            data = self.request.recv(512)
                            recvd_size += len(data)
                            recv_data += data
                    pic_md5 = hashlib.md5(recv_data).hexdigest()
                    if img_md5 == pic_md5:
                        fp.write(recv_data)
                        print('%s send over'% new_filename)
                        self.request.sendall('file send over!'.encode('utf-8'))
                    else:
                        print('%s send wrong!'% new_filename)
                        self.request.sendall('file send wrong!'.encode('utf-8'))
                if new_filename:
                    self.detect(new_filename,dirpath)
            else:
                print('close')
                break

    def detect(self,new_filename,dirpath):
        dataset = LoadImages(dirpath.decode(), img_size=opt.img_size)
        if dataset:
            for path, img, im0s, vid_cap in dataset:
                img = torch.from_numpy(img).to(device)
                img = img.half() if half else img.float()  # uint8 to fp16/32
                img /= 255.0  # 0 - 255 to 0.0 - 1.0
                if img.ndimension() == 3:
                    img = img.unsqueeze(0)
                # Inference
                pred = model(img, augment=opt.augment)[0]
                # Apply NMS
                pred = non_max_suppression(pred, opt.conf_thres, opt.iou_thres, classes=opt.classes, agnostic=opt.agnostic_nms)
                # Process detections
                for i, det in enumerate(pred):  # detections per image
                    p, s, im0 = path, '', im0s
                    gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
                    if det is not None and len(det):
                        det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()
                        dt_boxes, rec_res = [],[] 
                        for *xyxy, conf, cls in reversed(det):
                            xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                            line = (cls, conf, *xywh) if opt.save_conf else (cls, *xywh)  # label format
                            res = ('%g ' * len(line)) % line
                            res = res.split()
                            rec_res.append(names[int(cls)])
                            dt_boxes.append((res[1],res[2],res[3],res[4]))
                        send_data = str((dt_boxes, rec_res)).encode()
                        self.request.sendall(str(len(send_data)).encode())
                        client_news = self.request.recv(512)
                        self.request.sendall(send_data)
                        print('done!')
                        try:
                            os.remove(new_filename)
                        except PermissionError as e:
                            print(e)
                            os.remove(new_filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default='weights/jj_best.pt', help='model.pt path(s)')
    parser.add_argument('--source', type=str, default=r'tmp', help='source')  # file/folder, 0 for webcam
    parser.add_argument('--img-size', type=int, default=640, help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float, default=0.6, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.5, help='IOU threshold for NMS')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='display results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
    parser.add_argument('--save-dir', type=str, default='inference/output', help='directory to save results')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --class 0, or --class 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--update', action='store_true', help='update all models')
    opt = parser.parse_args()
    out, source, weights, view_img, save_txt, imgsz = \
        opt.save_dir, opt.source, opt.weights, opt.view_img, opt.save_txt, opt.img_size

    # Initialize
    set_logging()
    device = select_device(opt.device)
    # if os.path.exists(out):  # output dir
    #     shutil.rmtree(out)  # delete dir
    # os.makedirs(out)  # make new dir
    half = device.type != 'cpu'  # half precision only supported on CUDA

    # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    imgsz = check_img_size(imgsz, s=model.stride.max())  # check img_size
    if half:
        model.half()  # to FP16

    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(names))]

    # Run inference
    t0 = time.time()
    img = torch.zeros((1, 3, imgsz, imgsz), device=device)  # init img
    _ = model(img.half() if half else img) if device.type != 'cpu' else None  # run once

    ADDR = ('192.168.1.6',9999)
    server = ThreadingTCPServer(ADDR,Handler)  #参数为监听地址和已建立连接的处理类
    print('listening')
    server.serve_forever()  #监听，建立好TCP连接后，为该连接创建新的socket和线程，并由处理类中的handle方法处理
    print(server)






