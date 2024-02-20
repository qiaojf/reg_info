import numpy as np
import json
from xml.dom.minidom import Document
from tqdm import tqdm
import os

class ReadAnno:
    def __init__(self, json_path, process_mode="rectangle"):
        self.json_data = json.load(open(json_path))
        self.filename = self.json_data['imagePath']
        self.width = self.json_data['imageWidth']
        self.height = self.json_data['imageHeight']

        self.coordis = []
        assert process_mode in ["rectangle", "polygon"]
        if process_mode == "rectangle":
            self.process_polygon_shapes()
        elif process_mode == "polygon":
            self.process_polygon_shapes()

    def process_rectangle_shapes(self):
        for single_shape in self.json_data['shapes']:
            bbox_class = single_shape['label']
            xmin = single_shape['points'][0][0]
            ymin = single_shape['points'][0][1]
            xmax = single_shape['points'][1][0]
            ymax = single_shape['points'][1][1]
            self.coordis.append([xmin, ymin, xmax, ymax, bbox_class])

    def process_polygon_shapes(self):
        for single_shape in self.json_data['shapes']:
            bbox_class = single_shape['label']
            temp_points = []
            for couple_point in single_shape['points']:
                x = float(couple_point[0])
                y = float(couple_point[1])
                temp_points.append([x, y])
            temp_points = np.array(temp_points)
            xmin, ymin = temp_points.min(axis=0)
            xmax, ymax = temp_points.max(axis=0)
            self.coordis.append([xmin, ymin, xmax, ymax, bbox_class])

    def get_width_height(self):
        return self.width, self.height

    def get_filename(self):
        return self.filename

    def get_coordis(self):
        return self.coordis


class CreateAnno:
    def __init__(self, ):
        self.doc = Document()  # 创建DOM文档对象
        self.anno = self.doc.createElement('annotation')  # 创建根元素
        self.doc.appendChild(self.anno)

        self.add_folder()
        self.add_path()
        self.add_source()
        self.add_segmented()

        # self.add_filename()
        # self.add_pic_size(width_text_str=str(width), height_text_str=str(height), depth_text_str=str(depth))

    def add_folder(self, floder_text_str='JPEGImages'):
        floder = self.doc.createElement('floder')  ##建立自己的开头
        floder_text = self.doc.createTextNode(floder_text_str)  ##建立自己的文本信息
        floder.appendChild(floder_text)  ##自己的内容
        self.anno.appendChild(floder)

    def add_filename(self, filename_text_str='00000.jpg'):
        filename = self.doc.createElement('filename')
        filename_text = self.doc.createTextNode(filename_text_str)
        filename.appendChild(filename_text)
        self.anno.appendChild(filename)

    def add_path(self, path_text_str="None"):
        path = self.doc.createElement('path')
        path_text = self.doc.createTextNode(path_text_str)
        path.appendChild(path_text)
        self.anno.appendChild(path)

    def add_source(self, database_text_str="Unknow"):
        source = self.doc.createElement('source')
        database = self.doc.createElement('database')
        database_text = self.doc.createTextNode(database_text_str)  # 元素内容写入
        database.appendChild(database_text)
        source.appendChild(database)
        self.anno.appendChild(source)

    def add_pic_size(self, width_text_str="0", height_text_str="0", depth_text_str="3"):
        size = self.doc.createElement('size')
        width = self.doc.createElement('width')
        width_text = self.doc.createTextNode(width_text_str)  # 元素内容写入
        width.appendChild(width_text)
        size.appendChild(width)

        height = self.doc.createElement('height')
        height_text = self.doc.createTextNode(height_text_str)
        height.appendChild(height_text)
        size.appendChild(height)

        depth = self.doc.createElement('depth')
        depth_text = self.doc.createTextNode(depth_text_str)
        depth.appendChild(depth_text)
        size.appendChild(depth)

        self.anno.appendChild(size)

    def add_segmented(self, segmented_text_str="0"):
        segmented = self.doc.createElement('segmented')
        segmented_text = self.doc.createTextNode(segmented_text_str)
        segmented.appendChild(segmented_text)
        self.anno.appendChild(segmented)

    def add_object(self,
                   name_text_str="None",
                   xmin_text_str="0",
                   ymin_text_str="0",
                   xmax_text_str="0",
                   ymax_text_str="0",
                   pose_text_str="Unspecified",
                   truncated_text_str="0",
                   difficult_text_str="0"):
        object = self.doc.createElement('object')
        name = self.doc.createElement('name')
        name_text = self.doc.createTextNode(name_text_str)
        name.appendChild(name_text)
        object.appendChild(name)

        pose = self.doc.createElement('pose')
        pose_text = self.doc.createTextNode(pose_text_str)
        pose.appendChild(pose_text)
        object.appendChild(pose)

        truncated = self.doc.createElement('truncated')
        truncated_text = self.doc.createTextNode(truncated_text_str)
        truncated.appendChild(truncated_text)
        object.appendChild(truncated)

        difficult = self.doc.createElement('difficult')
        difficult_text = self.doc.createTextNode(difficult_text_str)
        difficult.appendChild(difficult_text)
        object.appendChild(difficult)

        bndbox = self.doc.createElement('bndbox')
        xmin = self.doc.createElement('xmin')
        xmin_text = self.doc.createTextNode(xmin_text_str)
        xmin.appendChild(xmin_text)
        bndbox.appendChild(xmin)

        ymin = self.doc.createElement('ymin')
        ymin_text = self.doc.createTextNode(ymin_text_str)
        ymin.appendChild(ymin_text)
        bndbox.appendChild(ymin)

        xmax = self.doc.createElement('xmax')
        xmax_text = self.doc.createTextNode(xmax_text_str)
        xmax.appendChild(xmax_text)
        bndbox.appendChild(xmax)

        ymax = self.doc.createElement('ymax')
        ymax_text = self.doc.createTextNode(ymax_text_str)
        ymax.appendChild(ymax_text)
        bndbox.appendChild(ymax)
        object.appendChild(bndbox)

        self.anno.appendChild(object)

    def get_anno(self):
        return self.anno

    def get_doc(self):
        return self.doc

    def save_doc(self, save_path):
        with open(save_path, "w") as f:
            self.doc.writexml(f, indent='\t', newl='\n', addindent='\t', encoding='utf-8')


def json_transform_xml(json_path, xml_path, process_mode="rectangle"):
    json_path = json_path
    json_anno = ReadAnno(json_path, process_mode=process_mode)
    width, height = json_anno.get_width_height()
    filename = json_anno.get_filename()
    coordis = json_anno.get_coordis()

    xml_anno = CreateAnno()
    xml_anno.add_filename(filename)
    xml_anno.add_pic_size(width_text_str=str(width), height_text_str=str(height), depth_text_str=str(3))
    for xmin, ymin, xmax, ymax, label in coordis:
        xml_anno.add_object(name_text_str=str(label),
                            xmin_text_str=str(int(xmin)),
                            ymin_text_str=str(int(ymin)),
                            xmax_text_str=str(int(xmax)),
                            ymax_text_str=str(int(ymax)))

    xml_anno.save_doc(xml_path)


# if __name__ == "__main__":
#     root_json_dir = r"./json/"  # json的路径
#     root_save_xml_dir = r"./label/"  # xml的保存路径
#     for json_filename in tqdm(os.listdir(root_json_dir)):
#         if json_filename.split('.')[-1]=='json':
#             json_path = os.path.join(root_json_dir, json_filename)
#             save_xml_path = os.path.join(root_save_xml_dir, json_filename.replace(".json", ".xml"))
#             try:
#                 json_transform_xml(json_path, save_xml_path, process_mode="rectangle")   # labelme原数据的标注方式(矩形rectangle和多边形polygon)
#             except json.decoder.JSONDecodeError as e:
#                 print(e)
#                 continue




 
import os
import numpy as np
import codecs
import json
from glob import glob
import cv2
import shutil
from sklearn.model_selection import train_test_split
#1.标签路径
labelme_path = "E:/Download/newdata/"              #原始labelme标注数据路径
saved_path = "./label/"                #保存路径
 
#2.创建要求文件夹
if not os.path.exists(saved_path + "Annotations"):
    os.makedirs(saved_path + "Annotations")
if not os.path.exists(saved_path + "JPEGImages/"):
    os.makedirs(saved_path + "JPEGImages/")
if not os.path.exists(saved_path + "ImageSets/Main/"):
    os.makedirs(saved_path + "ImageSets/Main/")
    
##3.获取待处理文件
#files = glob(labelme_path + "*.json")
#print(files)
#files = [i.split("/")[-1].split(".json")[0] for i in files]
 
#4.读取标注信息并写入 xml
#for json_file_ in files:
for json_file_ in os.listdir(labelme_path):
    if('.json' not in json_file_):
        continue
    else:
        json_file_ = json_file_.split('.json')[0]
    print(json_file_)
    json_filename = os.path.join(labelme_path , json_file_ + ".json")
    print(json_filename)
    json_file = json.load(open(json_filename,"r",encoding="utf-8"))
    print(os.path.join(labelme_path , json_file_ +".jpg"))
    height, width, channels = cv2.imread(os.path.join(labelme_path , json_file_ +".jpg")).shape
    with codecs.open(saved_path + "Annotations/"+json_file_ + ".xml","w","utf-8") as xml:
        xml.write('<annotation>\n')
        xml.write('\t<folder>' + 'UAV_data' + '</folder>\n')
        xml.write('\t<filename>' + json_file_ + ".jpg" + '</filename>\n')
        xml.write('\t<source>\n')
        xml.write('\t\t<database>The UAV autolanding</database>\n')
        xml.write('\t\t<annotation>UAV AutoLanding</annotation>\n')
        xml.write('\t\t<image>flickr</image>\n')
        xml.write('\t\t<flickrid>NULL</flickrid>\n')
        xml.write('\t</source>\n')
        xml.write('\t<owner>\n')
        xml.write('\t\t<flickrid>NULL</flickrid>\n')
        xml.write('\t\t<name>Yuanyiqin</name>\n')
        xml.write('\t</owner>\n')
        xml.write('\t<size>\n')
        xml.write('\t\t<width>'+ str(width) + '</width>\n')
        xml.write('\t\t<height>'+ str(height) + '</height>\n')
        xml.write('\t\t<depth>' + str(channels) + '</depth>\n')
        xml.write('\t</size>\n')
        xml.write('\t\t<segmented>0</segmented>\n')
        for multi in json_file["shapes"]:
            points = np.array(multi["points"])
            xmin = min(points[:,0])
            xmax = max(points[:,0])
            ymin = min(points[:,1])
            ymax = max(points[:,1])
            label = multi["label"]
            if xmax <= xmin:
                pass
            elif ymax <= ymin:
                pass
            else:
                xml.write('\t<object>\n')
                xml.write('\t\t<name>'+str(label)+'</name>\n')
                xml.write('\t\t<pose>Unspecified</pose>\n')
                xml.write('\t\t<truncated>1</truncated>\n')
                xml.write('\t\t<difficult>0</difficult>\n')
                xml.write('\t\t<bndbox>\n')
                xml.write('\t\t\t<xmin>' + str(xmin) + '</xmin>\n')
                xml.write('\t\t\t<ymin>' + str(ymin) + '</ymin>\n')
                xml.write('\t\t\t<xmax>' + str(xmax) + '</xmax>\n')
                xml.write('\t\t\t<ymax>' + str(ymax) + '</ymax>\n')
                xml.write('\t\t</bndbox>\n')
                xml.write('\t</object>\n')
                print(json_filename,xmin,ymin,xmax,ymax,label)
        xml.write('</annotation>')
        
#5.复制图片到 VOC2007/JPEGImages/下
image_files = glob(labelme_path + "*.jpg")
print("copy image files to VOC007/JPEGImages/")
for image in image_files:
    shutil.copy(image,saved_path +"JPEGImages/")
    
#6.split files for txt
txtsavepath = saved_path + "ImageSets/Main/"
ftrainval = open(txtsavepath+'/trainval.txt', 'w')
ftest = open(txtsavepath+'/test.txt', 'w')
ftrain = open(txtsavepath+'/train.txt', 'w')
fval = open(txtsavepath+'/val.txt', 'w')
total_files = glob("./label/Annotations/*.xml")
total_files = [i.split("/")[-1].split(".xml")[0] for i in total_files]
#test_filepath = ""
for file in total_files:
    ftrainval.write(file + "\n")
#test
#for file in os.listdir(test_filepath):
#    ftest.write(file.split(".jpg")[0] + "\n")
#split
train_files,val_files = train_test_split(total_files,test_size=0.15,random_state=42)
#train
for file in train_files:
    ftrain.write(file + "\n")
#val
for file in val_files:
    fval.write(file + "\n")
 
ftrainval.close()
ftrain.close()
fval.close()












