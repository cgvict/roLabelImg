#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

try:
  from lxml import etree
  print("running with lxml.etree")
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
    print("running with cElementTree on Python 2.5+")
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as etree
      print("running with ElementTree on Python 2.5+")
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as etree
        print("running with cElementTree")
      except ImportError:
        try:
          # normal ElementTree install
          import elementtree.ElementTree as etree
          print("running with ElementTree")
        except ImportError:
          print("Failed to import ElementTree from any known place")

import codecs
import math

XML_EXT = '.xml'

class PascalVocWriter:

    def __init__(self, foldername, filename, imgSize,databaseSrc='Unknown', localImgPath=None):
        self.foldername = foldername
        self.filename = filename
        self.databaseSrc = databaseSrc
        self.imgSize = imgSize
        self.boxlist = []
        self.roboxlist = []
        self.localImgPath = localImgPath
        self.verified = False


    def prettify(self, elem):
        """
            Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, 'utf8')
        root = etree.fromstring(rough_string)
        try:
            return etree.tostring(root, pretty_print=True)
        except TypeError:
            return etree.tostring(root)

    def genXML(self):
        """
            Return XML root
        """
        # Check conditions
        if self.filename is None or \
                self.foldername is None or \
                self.imgSize is None:
            return None

        top = Element('annotation')
        top.set('verified', 'yes' if self.verified else 'no')

        folder = SubElement(top, 'folder')
        folder.text = self.foldername

        filename = SubElement(top, 'filename')
        filename.text = self.filename

        localImgPath = SubElement(top, 'path')
        localImgPath.text = self.localImgPath

        source = SubElement(top, 'source')
        database = SubElement(source, 'database')
        database.text = self.databaseSrc

        size_part = SubElement(top, 'size')
        width = SubElement(size_part, 'width')
        height = SubElement(size_part, 'height')
        depth = SubElement(size_part, 'depth')
        width.text = str(self.imgSize[1])
        height.text = str(self.imgSize[0])
        if len(self.imgSize) == 3:
            depth.text = str(self.imgSize[2])
        else:
            depth.text = '1'

        segmented = SubElement(top, 'segmented')
        segmented.text = '0'
        return top

    def addBndBox(self, xmin, ymin, xmax, ymax, name, difficult):
        bndbox = {'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax}
        bndbox['name'] = name
        bndbox['difficult'] = difficult
        self.boxlist.append(bndbox)

    # You Hao 2017/06/21
    # add to analysis robndbox
    def addRotatedBndBox(self, cx, cy, w, h, angle, name, difficult):
        robndbox = {'cx': cx, 'cy': cy, 'w': w, 'h': h, 'angle': angle}
        robndbox['name'] = name
        robndbox['difficult'] = difficult
        self.roboxlist.append(robndbox)

    def appendObjects(self, top):
        for each_object in self.boxlist:
            object_item = SubElement(top, 'object')
            typeItem = SubElement(object_item, 'type')
            typeItem.text = "bndbox"
            name = SubElement(object_item, 'name')
            try:
                name.text = unicode(each_object['name'])
            except NameError:
                # Py3: NameError: name 'unicode' is not defined
                name.text = each_object['name']
            pose = SubElement(object_item, 'pose')
            pose.text = "Unspecified"
            truncated = SubElement(object_item, 'truncated')
            if int(each_object['ymax']) == int(self.imgSize[0]) or (int(each_object['ymin'])== 1):
                truncated.text = "1" # max == height or min
            elif (int(each_object['xmax'])==int(self.imgSize[1])) or (int(each_object['xmin'])== 1):
                truncated.text = "1" # max == width or min
            else:
                truncated.text = "0"
            difficult = SubElement(object_item, 'difficult')
            difficult.text = str( bool(each_object['difficult']) & 1 )            
            bndbox = SubElement(object_item, 'bndbox')
            xmin = SubElement(bndbox, 'xmin')
            xmin.text = str(each_object['xmin'])
            ymin = SubElement(bndbox, 'ymin')
            ymin.text = str(each_object['ymin'])
            xmax = SubElement(bndbox, 'xmax')
            xmax.text = str(each_object['xmax'])
            ymax = SubElement(bndbox, 'ymax')
            ymax.text = str(each_object['ymax'])

        # You Hao 2017/06/21
        # add to store robndbox
        for each_object in self.roboxlist:
            object_item = SubElement(top, 'object')
            typeItem = SubElement(object_item, 'type')
            typeItem.text = "robndbox"
            name = SubElement(object_item, 'name')
            try:
                name.text = unicode(each_object['name'])
            except NameError:
                # Py3: NameError: name 'unicode' is not defined
                name.text = each_object['name']
            pose = SubElement(object_item, 'pose')
            pose.text = "Unspecified"
            truncated = SubElement(object_item, 'truncated')
            # if int(each_object['ymax']) == int(self.imgSize[0]) or (int(each_object['ymin'])== 1):
            #     truncated.text = "1" # max == height or min
            # elif (int(each_object['xmax'])==int(self.imgSize[1])) or (int(each_object['xmin'])== 1):
            #     truncated.text = "1" # max == width or min
            # else:
            truncated.text = "0"
            difficult = SubElement(object_item, 'difficult')
            difficult.text = str( bool(each_object['difficult']) & 1 )
            robndbox = SubElement(object_item, 'robndbox')
            cx = SubElement(robndbox, 'cx')
            cx.text = str(each_object['cx'])
            cy = SubElement(robndbox, 'cy')
            cy.text = str(each_object['cy'])
            w = SubElement(robndbox, 'w')
            w.text = str(each_object['w'])
            h = SubElement(robndbox, 'h')
            h.text = str(each_object['h'])
            angle = SubElement(robndbox, 'angle')
            angle.text = str(each_object['angle'])

    def save(self, targetFile=None):
        root = self.genXML()
        self.appendObjects(root)
        out_file = None
        if targetFile is None:
            out_file = codecs.open(
                self.filename + XML_EXT, 'w', encoding='utf-8')
        else:
            out_file = codecs.open(targetFile, 'w', encoding='utf-8')

        prettifyResult = self.prettify(root)
        out_file.write(prettifyResult.decode('utf8'))
        out_file.close()


class PascalVocReader:

    def __init__(self, filepath):
        # shapes type:
        # [labbel, [(x1,y1), (x2,y2), (x3,y3), (x4,y4)], color, color, difficult]
        self.shapes = []
        self.filepath = filepath
        self.verified = False
        self.parseXML()

    def getShapes(self):
        return self.shapes

    def addShape(self, label, bndbox, difficult):
        xmin = int(bndbox.find('xmin').text)
        ymin = int(bndbox.find('ymin').text)
        xmax = int(bndbox.find('xmax').text)
        ymax = int(bndbox.find('ymax').text)
        points = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
        self.shapes.append((label, points, 0, False, None, None, difficult))

    # You Hao 2017/06/21
    # add to analysis robndbox load from xml
    def addRotatedShape(self, label, robndbox, difficult):
        cx = float(robndbox.find('cx').text)
        cy = float(robndbox.find('cy').text)
        w = float(robndbox.find('w').text)
        h = float(robndbox.find('h').text)
        angle = float(robndbox.find('angle').text)

        p0x,p0y = self.rotatePoint(cx,cy, cx - w/2, cy - h/2, -angle)
        p1x,p1y = self.rotatePoint(cx,cy, cx + w/2, cy - h/2, -angle)
        p2x,p2y = self.rotatePoint(cx,cy, cx + w/2, cy + h/2, -angle)
        p3x,p3y = self.rotatePoint(cx,cy, cx - w/2, cy + h/2, -angle)

        points = [(p0x, p0y), (p1x, p1y), (p2x, p2y), (p3x, p3y)]
        self.shapes.append((label, points, angle, True, None, None, difficult))

    def rotatePoint(self, xc,yc, xp,yp, theta):        
        xoff = xp-xc;
        yoff = yp-yc;

        cosTheta = math.cos(theta)
        sinTheta = math.sin(theta)
        pResx = cosTheta * xoff + sinTheta * yoff
        pResy = - sinTheta * xoff + cosTheta * yoff
        # pRes = (xc + pResx, yc + pResy)
        return xc+pResx,yc+pResy

    def parseXML(self):
        assert self.filepath.endswith(XML_EXT), "Unsupport file format"
        parser = etree.XMLParser(encoding='utf-8')
        xmltree = ElementTree.parse(self.filepath, parser=parser).getroot()
        filename = xmltree.find('filename').text
        try:
            verified = xmltree.attrib['verified']
            if verified == 'yes':
                self.verified = True
        except KeyError:
            self.verified = False

        for object_iter in xmltree.findall('object'):
            typeItem = object_iter.find('type')

            # print(typeItem.text)
            if typeItem.text == 'bndbox':
                bndbox = object_iter.find("bndbox")
                label = object_iter.find('name').text
                # Add chris
                difficult = False
                if object_iter.find('difficult') is not None:
                    difficult = bool(int(object_iter.find('difficult').text))
                self.addShape(label, bndbox, difficult)

            # You Hao 2017/06/21
            # add to load robndbox
            elif typeItem.text == 'robndbox':
                robndbox = object_iter.find('robndbox')
                label = object_iter.find('name').text
                difficult = False
                if object_iter.find('difficult') is not None:
                    difficult = bool(int(object_iter.find('difficult').text))
                self.addRotatedShape(label, robndbox, difficult)
            
            else: 
                pass

        return True
