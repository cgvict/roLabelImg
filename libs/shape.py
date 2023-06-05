#!/usr/bin/python
# -*- coding: utf-8 -*-


try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

from lib import distance
import math
from colors import *

DEFAULT_LINE_COLOR = QColor(0, 255, 0, 128)
DEFAULT_FILL_COLOR = QColor(255, 0, 0, 128)
DEFAULT_SELECT_LINE_COLOR = QColor(255, 255, 255)
DIRECTION_ARROW_COLOR = QColor(255, 0, 0)
DEFAULT_SELECT_FILL_COLOR = QColor(0, 128, 255, 155)
DEFAULT_VERTEX_FILL_COLOR = QColor(0, 255, 0, 255)
DEFAULT_HVERTEX_FILL_COLOR = QColor(255, 0, 0)
ARROW_LENGTH = 10
ARROW_ANGLE = 0.5

class Shape(object):
    P_SQUARE, P_ROUND = range(2)

    MOVE_VERTEX, NEAR_VERTEX = range(2)

    # The following class variables influence the drawing
    # of _all_ shape objects.
    line_color = DEFAULT_LINE_COLOR
    fill_color = DEFAULT_FILL_COLOR
    select_line_color = DEFAULT_SELECT_LINE_COLOR
    select_fill_color = DEFAULT_SELECT_FILL_COLOR
    vertex_fill_color = DEFAULT_VERTEX_FILL_COLOR
    hvertex_fill_color = DEFAULT_HVERTEX_FILL_COLOR
    point_type = P_ROUND
    point_size = 8
    scale = 1.0

    def __init__(self, label=None, line_color=None,difficult = False):
        self.label = label
        self.points = []
        self.fill = False
        self.selected = False
        self.difficult = difficult

        self.direction = 0  # added by hy
        self.center = None # added by hy
        self.isRotated = True 

        self._highlightIndex = None
        self._highlightMode = self.NEAR_VERTEX
        self._highlightSettings = {
            self.NEAR_VERTEX: (4, self.P_ROUND),
            self.MOVE_VERTEX: (1.5, self.P_SQUARE),
        }

        self._closed = False

        if line_color is not None:
            # Override the class line_color attribute
            # with an object attribute. Currently this
            # is used for drawing the pending line a different color.
            self.line_color = line_color

        self.labels = ['postive_face', 'negative_face', 'open_eye', 'closed_eye', 'open_mouth', 'closed_mouth', 'phone_and_hand']


    def rotate(self, theta):
        for i, p in enumerate(self.points):
            self.points[i] = self.rotatePoint(p, theta)
        self.direction -= theta
        self.direction = self.direction % (2 * math.pi)

    def rotatePoint(self, p, theta):
        order = p-self.center
        cosTheta = math.cos(theta)
        sinTheta = math.sin(theta)
        pResx = cosTheta * order.x() + sinTheta * order.y()
        pResy = - sinTheta * order.x() + cosTheta * order.y()
        pRes = QPointF(self.center.x() + pResx, self.center.y() + pResy)
        return pRes

    def close(self):
        self.center = QPointF((self.points[0].x()+self.points[2].x()) / 2, (self.points[0].y()+self.points[2].y()) / 2)
        # print("refresh center!")
        self._closed = True

    def reachMaxPoints(self):
        if len(self.points) >= 4:
            return True
        return False

    def addPoint(self, point):
        if self.points and len(self.points) == 4 and point == self.points[0]:
            self.close()
        else:
            self.points.append(point)

    def popPoint(self):
        if self.points:
            return self.points.pop()
        return None

    def isClosed(self):
        return self._closed

    def setOpen(self):
        self._closed = False

    def paint(self, painter):
        if self.points:
            label_index = 7
            for i in range(len(self.labels)):
                if self.label == self.labels[i]:
                    label_index = i
                    break
            color = colors(label_index)#self.select_line_color if self.selected else self.line_color
            #print(self.label, label_index, color)
            pen = QPen(color)
            # Try using integer sizes for smoother drawing(?)
            pen.setWidth(max(1, int(round(1.0 / self.scale))))
            painter.setPen(pen)

            line_path = QPainterPath()
            vrtx_path = QPainterPath()

            line_path.moveTo(self.points[0])
            # Uncommenting the following line will draw 2 paths
            # for the 1st vertex, and make it non-filled, which
            # may be desirable.
            #self.drawVertex(vrtx_path, 0)

            for i, p in enumerate(self.points):
                line_path.lineTo(p)
                # print('shape paint points (%d, %d)' % (p.x(), p.y()))
                # if(i == len(self.points) - 1):
                #     pen.setColor(DIRECTION_ARROW_COLOR)
                #     painter.setPen(pen)
                # cur_line = QLineF()
                # cur_line.setP1(self.points[i])
                # cur_line.setP2(self.points[(i + 1) % (len(self.points))])
                # painter.drawLine(cur_line)
                self.drawVertex(vrtx_path, i)
        
            if self.isClosed():
                line_path.lineTo(self.points[0])

            # dir_path = QPainterPath()
            # tempP = self.points[0]+QPointF(10,10)
            # print('direction2 is %lf, a os %lf' % (self.direction,math.tan(self.direction)))
            # dir_path.moveTo(tempP)
            # dir_path.lineTo(tempP + QPointF(10, (10-tempP.x())* math.tan(self.direction)+tempP.y()))
            # painter.drawPath(dir_path)

            painter.drawPath(line_path)
            painter.drawPath(vrtx_path)
            painter.fillPath(vrtx_path, self.vertex_fill_color)

            
            if len(self.points) == 4 and self.isRotated:
                pen.setColor(DIRECTION_ARROW_COLOR)
                painter.setPen(pen)
                center = (self.points[0]+self.points[2]) / 2 # the center of rectangle
                toward_point = (self.points[3] + self.points[0]) / 2 # the end point in the direction

                arrow_center = QLineF(toward_point, center)
                painter.drawLine(arrow_center)

                arrow_center.setLength(ARROW_LENGTH)
                arrow_center_x = arrow_center.x2() - arrow_center.x1()
                arrow_center_y = arrow_center.y2() - arrow_center.y1()
                
                arrow_left_p2_x = arrow_center_x * math.cos(ARROW_ANGLE) - arrow_center_y * math.sin(ARROW_ANGLE)
                arrow_left_p2_y = arrow_center_x * math.sin(ARROW_ANGLE) + arrow_center_y * math.cos(ARROW_ANGLE)
                arrow_center.setP2(QPointF(arrow_center.x1() + arrow_left_p2_x, arrow_center.y1() + arrow_left_p2_y))
                painter.drawLine(arrow_center)

                arrow_right_p2_x = arrow_center_x * math.cos(-ARROW_ANGLE) - arrow_center_y * math.sin(-ARROW_ANGLE)
                arrow_right_p2_y = arrow_center_x * math.sin(-ARROW_ANGLE) + arrow_center_y * math.cos(-ARROW_ANGLE)
                arrow_center.setP2(QPointF(arrow_center.x1() + arrow_right_p2_x, arrow_center.y1() + arrow_right_p2_y))
                painter.drawLine(arrow_center)

                pen.setColor(color)
                painter.setPen(pen)


            #if self.fill:
            #    color = self.select_fill_color if self.selected else self.fill_color
            #    painter.fillPath(line_path, color)

            if self.center is not None:
                center_path = QPainterPath()
                d = self.point_size / self.scale
                center_path.addRect(self.center.x() - d / 2, self.center.y() - d / 2, d, d)
                painter.drawPath(center_path)
                if self.isRotated:
                    painter.fillPath(center_path, self.vertex_fill_color)
                else:
                    painter.fillPath(center_path, QColor(0, 0, 0))

    def paintNormalCenter(self, painter):
        if self.center is not None:
            center_path = QPainterPath()
            d = self.point_size / self.scale
            center_path.addRect(self.center.x() - d / 2, self.center.y() - d / 2, d, d)
            painter.drawPath(center_path)
            if not self.isRotated:
                painter.fillPath(center_path, QColor(0, 0, 0))

    def drawVertex(self, path, i):
        d = self.point_size / self.scale
        shape = self.point_type
        point = self.points[i]
        if i == self._highlightIndex:
            size, shape = self._highlightSettings[self._highlightMode]
            d *= size
        if self._highlightIndex is not None:
            self.vertex_fill_color = self.hvertex_fill_color
        else:
            self.vertex_fill_color = Shape.vertex_fill_color
        if shape == self.P_SQUARE:
            path.addRect(point.x() - d / 2, point.y() - d / 2, d, d)
        elif shape == self.P_ROUND:
            path.addEllipse(point, d / 2.0, d / 2.0)
        else:
            assert False, "unsupported vertex shape"
    # def drawVertex(self, path, center):
    #     pass

    def nearestVertex(self, point, epsilon):
        for i, p in enumerate(self.points):
            if distance(p - point) <= epsilon:
                return i
        return None

    def containsPoint(self, point):
        return self.makePath().contains(point)

    def makePath(self):
        path = QPainterPath(self.points[0])
        for p in self.points[1:]:
            path.lineTo(p)
        return path

    def boundingRect(self):
        return self.makePath().boundingRect()

    def moveBy(self, offset):
        self.points = [p + offset for p in self.points]

    def moveVertexBy(self, i, offset):
        self.points[i] = self.points[i] + offset

    def highlightVertex(self, i, action):
        self._highlightIndex = i
        self._highlightMode = action

    def highlightClear(self):
        self._highlightIndex = None

    def copy(self):
        shape = Shape("%s" % self.label)
        shape.points = [p for p in self.points]
        
        shape.center = self.center
        shape.direction = self.direction
        shape.isRotated = self.isRotated

        shape.fill = self.fill
        shape.selected = self.selected
        shape._closed = self._closed
        if self.line_color != Shape.line_color:
            shape.line_color = self.line_color
        if self.fill_color != Shape.fill_color:
            shape.fill_color = self.fill_color
        shape.difficult = self.difficult 
        return shape

    def __len__(self):
        return len(self.points)

    def __getitem__(self, key):
        return self.points[key]

    def __setitem__(self, key, value):
        self.points[key] = value
