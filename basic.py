"""
Created on Jan 29, 2010

@author: yaocheng
"""

import sys
import math

class Point(object):
    """Basic type representing point in 2-D space."""
    
    def __init__(self, x, y):
        """Initialize the point's x and y value."""
        self.x = x;
        self.y = y;
       
    '''def __eq__(self, other):
        """Compare whether two points' value are equal to each other."""
        try:
            if self.x == other.x and self.y == other.y:
                return True
            else:
                return False
        except AttributeError:
            print "point comparison eq: type error happened"
        
    def __ne__(self, other):
        """Compare whether two points' value are equal to each other."""
        try:
            if self.x != other.x or self.y != other.y:
                return True
            else:
                return False
        except AttributeError:
            print "point comparison ne: type error happened" '''
        
    def clone(self):
        """Return a deep copy of an existed point."""
        np = Point(self.x, self.y)
        return np
        
    @classmethod
    def interpolate(cls, p1, p2, t=0.5):
        if t >= 0 and t <= 1:
            deltaX = p2.x - p1.x
            deltaY = p2.y - p1.y
            return Point(p1.x + deltaX * t, p1.y + deltaY * t)
        else:
            print "Invalid t value"
            
    def relative_to(self, origin):
        """Return a new point object relative to point 'origin'."""
        print "blah"
        
        
class Segment(object):
    """Base class representing finite figure in 2-D space."""
    
    def __init__(self, a1, a2):
        """Initialize a segment with two ends."""
        self.a1 = a1
        self.a2 = a2
        self.approx_num = 0
        self.approx_points = []
        
    def point_at_t(self, t):
        """Doing nothing, overwritten in subclasses."""
        pass
        
    def get_approx_points(self, num):
        """Given the number of points used to approximate the segment, calculate
           these points.

           For a straight line, these approximate points are only used to
           calculate the distance between a point and this segment, but not for
           drawing (with PIL). For bezier curves, these points are for both
           usage."""
        self.approx_num = num
        self.approx_points.append(self.a1)
        step = 1.0 / num
        for i in range(1, num):
            # Specific "point_at_t" method defined in subclasses
            p = self.point_at_t(i * step)
            self.approx_points.append(p)
        self.approx_points.append(self.a2)
        
    def reverse(self):
        """Reverse the start(a1) and end point(a2) of a segment. If approximate points
           are calculated, reverse their order as well."""
        temp = self.a1
        self.a1 = self.a2
        self.a2 = temp
        if self.approx_points != []:
            self.approx_points.reverse()
        
        
class StraightLine(Segment):
    """Basic type representing straight line in 2-D space."""
    
    def __init__(self, a1=None, a2=None, slope=None, cross_y=None):
        """Initialize a straight line."""
        super(StraightLine, self).__init__(a1, a2)
        self.slope = slope
        self.cross_y = cross_y
        
    @classmethod
    def from_ab(cls, slope, cross_y):
        """Construct a straight line from a and b value."""
        sl= StraightLine(None, None, slope, cross_y)
        if slope == 0:
            sl.cross_x = None # do not cross x-axis
        else:
            sl.cross_x = -1.0 * cross_y / slope
        return sl
        
    @classmethod
    def from_points(cls, a1, a2):
        """Construct a straight line from two points."""
        sl = StraightLine(a1, a2, None, None)
        if a1.x == a2.x:
            sl.slope = sys.maxint # the value of "slope" is infinite
            sl.cross_y = None # do not cross y-axis
            sl.cross_x = a1.x
        elif a1.y == a2.y:
            sl.slope = 0
            sl.cross_y = a1.y
            sl.cross_x = None # do not cross x-axis
        else:
            sl.slope = (a1.y - a2.y) / (a1.x - a2.x)
            sl.cross_y = (a1.x * a2.y - a2.x * a1.y) / (a1.x - a2.x)
            sl.cross_x = -1.0 * sl.cross_y / sl.slope
        return sl
    
    def get_y_from_x(self, x):
        """Given an x, get y = ax + b."""
        if self.slope == sys.maxint:
            return None # means "y" can be any value
        else:
            return self.slope * x + self.cross_y
        
    def get_x_from_y(self, y):
        """Given an y, get x = (y - b) / a."""
        if self.slope == 0:
            return None # means "x" can be any value
        else:
            if self.slope == sys.maxint:
                return self.cross_x
            else:
                return 1.0 * (y - self.cross_y) / self.slope
                    
    def reverse(self):
        """Reverse the direction of a straight line."""
        if self.a1 is None or self.a2 is None:
            print "No sense to reverse a infinite straight line"
        else:
            super(StraightLine, self).reverse()
            
    def point_at_t(self, t):
        """Given a t value between 0 and 1, get the point from the finite line."""
        super(StraightLine, self).point_at_t(t)
        if self.a1 is None or self.a2 is None:
            print "The function is not applicable to an infinite straight line"
        else:
            if t < 0 or t > 1:
                print "Invalid t value"
            else:
                deltaX = self.a2.x - self.a1.x
                deltaY = self.a2.y - self.a2.y
                x = self.a1.x + deltaX * t
                y = self.a1.y + deltaY * t
                return Point(x, y)
                
    def drawing_coords(self, num):
        """Return the coordinates sequence that used (by PIL) to draw the finite
           straight line."""
        # Argument "num" is of no use in the case of straight line
        if self.a1 is None or self.a2 is None:
            print "No way to draw an infinite line"
        else:
            return [(self.a1.x, self.a1.y), (self.a2.x, self.a2.y)]
            
    @classmethod
    def cross(cls, sl1, sl2):
        """Get the cross point of two straight lines."""
        try:
            x = (sl2.cross_y - sl1.cross_y) / (sl1.slope - sl2.slope)
            y = (sl1.slope * sl2.cross_y - sl1.cross_y * sl2.slope) / (sl1.slope - sl2.slope)
            return Point(x, y)
        except ZeroDivisionError:
            print "Two straight lines are parallel to each other"
        except:
            print "Something wrong with lines' slope or cross_y, probably cross_y"
            
            
class QuadraticBezier(Segment):
    """Basic type representing quadratic bezier curve in 2-D space."""
    
    def __init__(self, a1, c, a2):
        """Initialize a quadratic bezier curve from start(a1), control(c) and end(a2) points."""
        super(QuadraticBezier, self).__init__(a1, a2)
        self.c = c
        
    def reverse(self):
        """Reverse the direction of the curve."""
        super(QuadraticBezier, self).reverse()
        
    def point_at_t(self, t):
        """Given a t value between 0 and 1, get the point from the curve."""
        super(QuadraticBezier, self).point_at_t(t)
        if t >= 0 and t <= 1:
            x = math.pow((1 - t), 2) * self.a1.x + \
                2 * (1 - t) * t * self.c.x + \
                math.pow(t, 2) * self.a2.x
            y = math.pow((1 - t), 2) * self.a1.y + \
                2 * (1 - t) * t * self.c.y + \
                math.pow(t, 2) * self.a2.y
            return Point(x, y)
        else:
            print "Invalid t value"

    def drawing_coords(self, num):
        """Return the coordinates sequence that used (by PIL) to approximately
           draw this quadratic bezier segment."""
        if self.approx_num != num:
            self.get_approx_points(num)
        coords = []
        for p in self.approx_points:
            coords.append((p.x, p.y))
        return coords
        
        
class CubicBezier(Segment):
    """Basic type representing cubic bezier curve in 2-D space."""
    
    def __init__(self, a1, c1, c2, a2):
        """Initialize a cubic bezier curve from start(a1), control1(c1), 
           control2(c2) and end(a2) points."""
        super(CubicBezier, self).__init__(a1, a2)
        self.c1 = c1
        self.c2 = c2
        
    def reverse(self):
        """Reverse the direction of the curve."""
        temp = self.c1
        self.c1 = self.c2
        self.c2 = temp
        super(CubicBezier, self).reverse()
        
    def point_at_t(self, t):
        """Given a t value between 0 and 1, get the point from the curve."""
        super(CubicBezier, self).point_at_t(t)
        if t >= 0 and t <= 1:
            x = math.pow((1 - t), 3) * self.a1.x + \
                3 * math.pow((1 - t), 2) * t * self.c1.x + \
                3 * (1 - t) * math.pow(t, 2) * self.c2.x + \
                math.pow(t, 3) * self.a2.x
            y = math.pow((1 - t), 3) * self.a1.y + \
                3 * math.pow((1 - t), 2) * t * self.c1.y + \
                3 * (1 - t) * math.pow(t, 2) * self.c2.y + \
                math.pow(t, 3) * self.a2.y
            return Point(x, y)
        else:
            print "Invalid t value"

    def drawing_coords(self, num):
        """Return the coordinates sequence that used (by PIL) to approximately
           draw this cubic bezier segment."""
        if self.approx_num != num:
            self.get_approx_points(num)
        coords = []
        for p in self.approx_points:
            coords.append((p.x, p.y))
        return coords
        
    def divide(self, factor=2):
        """Recursively divide the curve into two sub-curves for <factor> times."""
        sub_curves = []
        sub_curves.append(self)
        while factor > 0:
            temp = []
            for curve in sub_curves:
                a1 = curve.a1
                c1 = curve.c1
                c2 = curve.c2
                a2 = curve.a2
                a1c1 = Point.interpolate(a1, c1)
                c1c2 = Point.interpolate(c1, c2)
                c2a2 = Point.interpolate(c2, a2)
                a1c1c1c2 = Point.interpolate(a1c1, c1c2)
                c1c2c2a2 = Point.interpolate(c1c2, c2a2)
                a1c1c1c2c1c2c2a2 = Point.interpolate(a1c1c1c2, c1c2c2a2)
                sub_curve1 = CubicBezier(a1, a1c1, a1c1c1c2, a1c1c1c2c1c2c2a2)
                sub_curve2 = CubicBezier(a1c1c1c2c1c2c2a2, c1c2c2a2, c2a2, a2)
                temp.append(sub_curve1)
                temp.append(sub_curve2)
            sub_curves = temp
            factor -= 1
        return sub_curves
    
    def approximate(self):
        """Given a cubic bezier curve, get the quadratic approximation of it."""
        sl1 = StraightLine(self.a1, self.c1)
        sl2 = StraightLine(self.c2, self.a2)
        c = StraightLine.cross(sl1, sl2)
        return QuadraticBezier(self.a1, c, self.a2)
