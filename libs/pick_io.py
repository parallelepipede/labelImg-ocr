#!/usr/bin/env python
# -*- coding: utf8 -*-
import codecs, csv
import string
from libs.constants import DEFAULT_ENCODING
from os import mkdir, path
from json import dumps

TXT_EXT = '.txt'
JPG_EXT = '.jpg'
TSV_EXT = '.tsv'
ENCODE_METHOD = DEFAULT_ENCODING

class PickWriter:

    def __init__(self, folder_name : string, file_name : string, shapes, pillow_image):
        # Folder where all annotations are saved
        self.folder_name : string = folder_name
        # Name of the processed file without extension
        self.file_name : string = file_name
        # New name of the processed file without extension
        self.new_name : string = None
        # Pillow image of the processed file
        self.pillow_image = pillow_image
        # Registered shapes for the processed file
        self.shapes = shapes
        self.verified = False
        # Useful paths
        self.boxes_and_transcripts_path = path.join(self.folder_name, "boxes_and_transcripts")
        self.entities_path = path.join(self.folder_name, "entities")
        self.images_path = path.join(self.folder_name, "images")

    # Write a file with his name, extension and content
    def __write(self, filename, ext, content):
        out_file = codecs.open(filename + ext, 'w', encoding=ENCODE_METHOD)
        out_file.write(content)
        out_file.close()
    
    # Format coordinates of every points for pick annotation format
    def __format_coordinates(self,points):
        output = ''
        for point in points:
            output += str(round(point[0])) + ',' + str(round(point[1])) + ','
        return output
    
    def __print_shape(self,shape):
        return '1,' + self.__format_coordinates(shape['points']) + shape['transcript'] + ',' + shape['label'] + '\n'

    # Write boxes coordinates and transcripts of these boxes
    # index, box_coordinates (clockwise 8 values), transcripts, box_entity_types
    def __write_boxes_and_transcripts(self):
        content=""
        for shape in self.shapes:
            content += self.__print_shape(shape)
        self.__write(path.join(self.boxes_and_transcripts_path,self.new_name),TSV_EXT,content)
    
    # JSON list of the entites ({"entity_name": 'entity_value, ...})
    def __write_entities(self):
        content = {}
        for shape in self.shapes:
            content.update({shape['label']:shape['transcript']})
        self.__write(path.join(self.entities_path,self.new_name),TXT_EXT,str(dumps(content)))
    
    # JPG image of the object
    def __save_image(self):
        self.pillow_image.save(path.join(self.images_path,self.new_name+JPG_EXT))

    def __create_directories(self):
        print("Creating directory ", self.boxes_and_transcripts_path)
        mkdir(path.join(self.folder_name, "boxes_and_transcripts"))
        print("Creating directory ",self.entities_path)
        mkdir(self.entities_path)
        print("Creating directory ",self.images_path)
        mkdir(self.images_path)
    
    def __exists_directories(self):
        return path.exists(self.boxes_and_transcripts_path) and path.exists(self.entities_path) and path.exists(self.images_path)

    def __compute_new_filename(self):
        self.new_name = self.file_name.replace(".","")

    def save(self):
        self.__compute_new_filename()
        if not self.__exists_directories():
            self.__create_directories()
        self.__write_boxes_and_transcripts()
        self.__write_entities()
        self.__save_image()

class PickReader:
    def __init__(self, folder_name, file_name):
        # Folder where all annotations are saved
        self.folder_name = folder_name
        # Name of the processed file without extension
        self.file_name = file_name
        # shapes type:
        # [label, transcript, [(x1,y1), (x2,y2), (x3,y3), (x4,y4)], color, color, difficult]
        self.shapes = []
        # Useful paths
        self.boxes_and_transcripts_path = path.join(self.folder_name, "boxes_and_transcripts")
        # Actions
        self.__parse_pick_format()

    def get_shapes(self):
        return self.shapes
    
    def __add_shape(self, label, transcript, points):
        self.shapes.append((label, transcript, points, None, None, False))

    def __parse_pick_format(self):
        # Open file and parse file and save parsing in shape
        with open(path.join(self.boxes_and_transcripts_path,self.file_name+TSV_EXT),encoding=DEFAULT_ENCODING) as file:
            tsv_file = csv.reader(file, delimiter=",")
            for line in tsv_file:
                points = [(int(line[i]),int(line[i+1])) for i in range(1,9,2)]
                transcript = ",".join(line[9:-1])
                self.__add_shape(line[-1],transcript,points)