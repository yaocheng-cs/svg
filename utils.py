'''
Created on Apr 13, 2010

@author: yaocheng
'''

import sys
import math

class Distance(object):
    """A utility class containing functions for calculating distance between two 
       objects."""
    
    def __init__(self):
        """Constructor: doing nothing."""
        pass
        
    @classmethod
    def point_to_point(cls, p1, p2):
        """Calculate the distance between two points."""
        return math.sqrt(math.pow(p1.x - p2.x, 2) + math.pow(p1.y - p2.y, 2))
        
    @classmethod
    def point_to_seg(cls, p1, seg, num=20):
        """Calculate the distance between a point and a segment: the minimum
           distance between the given point and segment's approximate points is
           defined as the point-to-segment distance.
           If the number of points(num) specified here is bigger than segment's
           record, re-caculate segement's approximate points."""
        if seg.approx_num < num:
            seg.get_approx_points(num)
        point = None
        dist = sys.maxint
        for p in seg.approx_points:
            d = cls.point_to_point(p1, p)
            if d < dist:
                dist = d
                point = p
        return point, dist
        
    @classmethod
    def point_to_path(cls, p1, path, num=20):
        """Calculate the distance between a point and a path: the mimimum 
           distance between the given point and any segment of the path is 
           defined as the point-to-path distance."""
        point = None
        dist = sys.maxint
        for seg in path.segments:
            p, d = cls.point_to_seg(p1, seg, num)
            if d < dist:
                dist = d
                point = p
        return point, dist
