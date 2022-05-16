#!/usr/bin/env python
# -*- coding: utf8 -*-
import codecs
from libs.constants import DEFAULT_ENCODING
from os import mkdir, path

TXT_EXT = '.txt'
JPG_EXT = '.jpg'
TSV_EXT = '.tsv'
ENCODE_METHOD = DEFAULT_ENCODING

class PickWriter:

    def __init__(self, folder_name, file_name, shapes, pillow_image):
        # Folder where all annotations are saved
        self.folder_name = folder_name
        # Name of the processed file without extension
        self.file_name = file_name
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