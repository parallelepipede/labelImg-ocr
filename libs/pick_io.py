#!/usr/bin/env python
# -*- coding: utf8 -*-
from xml.etree import ElementTree
from lxml import etree
import codecs
from libs.constants import DEFAULT_ENCODING
from os import mkdir, path

TXT_EXT = '.txt'
CSV_EXT = '.csv'
JPG_EXT = '.jpg'
TSV_EXT = '.tsv'
ENCODE_METHOD = DEFAULT_ENCODING

class PickWriter:

    def __init__(self, folder_name, file_name, shapes, pillow_image, entities_list, database_src='Unknown', local_img_path=None):
        self.folder_name = folder_name
        self.file_name = file_name
        self.database_src = database_src
        self.pillow_image = pillow_image
        self.shapes = shapes
        self.local_img_path = local_img_path
        self.entities_list = entities_list
        self.verified = False
        self.boxes_and_transcripts_path = path.join(self.folder_name, "boxes_and_transcripts")
        self.entities_path = path.join(self.folder_name, "entities")
        self.images_path = path.join(self.folder_name, "images")

    def __write(self, filename, ext, content):
        out_file = codecs.open(filename + ext, 'w', encoding=ENCODE_METHOD)
        out_file.write(content)
        out_file.close()
    
    def __format_coordinates(self,points):
        output = ''
        for point in points:
            output += str(point[0]) + ',' + str(point[1])
        return output
    
    def __print_shape(self,shape):
        return '1,' + self.__format_coordinates(shape['points']) + ',' + shape['transcript'] + ',' + shape['label'] + '\n'

    # index, box_coordinates (clockwise 8 values), transcripts, box_entity_types
    def __write_boxes_and_transcripts(self):
        content=''
        for shape in self.shapes:
            content += self.__print_shape(shape)
        self.__write(path.join(self.boxes_and_transcripts_path,self.file_name),TSV_EXT,content)
    
    # JSON list of the entites ({"entity_name": 'entity_value, ...})
    def __write_entities(self):
        content = {}
        for shape in self.shapes:
            content.update({shape['label']:shape['transcript']})
        self.__write(path.join(self.entities_path,self.file_name),TXT_EXT,str(content))
    
    # JPG image of the object
    def __save_image(self):
        print("Image saved at ",path.join(self.images_path,self.file_name+JPG_EXT))
        self.pillow_image.save(path.join(self.images_path,self.file_name+JPG_EXT))
    
    def __create_samples_list(self):
        filename = self.folder_name + "samples_list"
        content = ""
        self.__write(filename,CSV_EXT,content)

    def __create_directories(self):
        print("Creating directory ", self.boxes_and_transcripts_path)
        mkdir(path.join(self.folder_name, "boxes_and_transcripts"))
        print("Creating directory ",self.entities_path)
        mkdir(self.entities_path)
        print("Creating directory ",self.images_path)
        mkdir(self.images_path)
    
    def __exists_directories(self):
        return path.exists(self.boxes_and_transcripts_path) and path.exists(self.entities_path) and path.exists(self.images_path)

    def save(self):
        if not self.__exists_directories():
            self.__create_directories()
        self.__write_boxes_and_transcripts()
        self.__write_entities()
        self.__save_image()
        #self.__create_samples_list()
    

class PickReader:

    def __init__(self, file_path):
        # shapes type:
        # [labbel, [(x1,y1), (x2,y2), (x3,y3), (x4,y4)], color, color, difficult]
        self.shapes = []
        self.file_path = file_path
        self.verified = False
        try:
            self.parse_xml()
        except:
            pass

    def get_shapes(self):
        return self.shapes

    def add_shape(self, label, bnd_box, difficult):
        x_min = int(float(bnd_box.find('xmin').text))
        y_min = int(float(bnd_box.find('ymin').text))
        x_max = int(float(bnd_box.find('xmax').text))
        y_max = int(float(bnd_box.find('ymax').text))
        points = [(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]
        self.shapes.append((label, points, None, None, difficult))

    def parse_xml(self):
        assert self.file_path.endswith(TXT_EXT), "Unsupported file format"
        parser = etree.XMLParser(encoding=ENCODE_METHOD)
        xml_tree = ElementTree.parse(self.file_path, parser=parser).getroot()
        filename = xml_tree.find('filename').text
        try:
            verified = xml_tree.attrib['verified']
            if verified == 'yes':
                self.verified = True
        except KeyError:
            self.verified = False

        for object_iter in xml_tree.findall('object'):
            bnd_box = object_iter.find("bndbox")
            label = object_iter.find('name').text
            # Add chris
            difficult = False
            if object_iter.find('difficult') is not None:
                difficult = bool(int(object_iter.find('difficult').text))
            self.add_shape(label, bnd_box, difficult)
        return True
