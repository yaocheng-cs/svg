'''
Created on Jan 27, 2010

@author: yaocheng
'''

from basic import Segment
from basic import StraightLine

class Path(object):
    """A continual route in 2-D space, may consist of finite line, curve and 
       other possible components(segments). Path can be closed or open."""
       
    def __init__(self):
        """Initialize an 'empty' path."""
        self.segments = []
        self.start = None
        self.end = None
        self.closed = False
        
    def extend(self, segment):
        """Extend an open path at the end, with one more segment."""
        #if self.closed:
        #    print "No sense to extend a closed path"
        #else:
        if not isinstance(segment, Segment):
            print "Invalid argument type to be a path segment"
            return
        self.segments.append(segment)
        if self.start == None:
            self.start = segment.a1
        self.end = segment.a2
            
    def unshift(self, segment):
        """Extend an open path before the start, with one more segment."""
        #if self.closed:
        #    print "No sense to unshift a closed path"
        #else:
        if not isinstance(segment, Segment):
            print "Invalid argument type to be a path segment"
            return
        self.segments.insert(0, segment)
        if self.end == None:
            self.end = segment.a2
        self.start = segment.a1
            
    def close(self):
        """Close the path by connecting 'start' and 'end' with a straight line, 
           then point self.end to the same thing as self.start pointed to."""
        #if self.closed:
        #    print "No sense to close an already closed path"
        #else:
        if self.end.x != self.start.x or self.end.y != self.start.y:
            close_seg = StraightLine.from_points(self.end, self.start)
            self.segments.append(close_seg)
        self.end = self.start
        self.closed = True
            
    def reverse(self):
        """Reverse the order of all segments in this path."""
        self.segments.reverse()
        for seg in self.segments:
            seg.reverse()
        temp = self.start
        self.start = self.end
        self.end = temp
        
    @classmethod
    def connect(cls, path1, path2):
        """Connect two paths to form a new path."""
        ns = StraightLine.from_points(path1.end, path2.start)
        np = Path()
        np.segments.extend(path1.segments)
        np.append(ns)
        np.segments.extend(path2.segments)
        np.start = path1.start
        np.end = path2.end
        return np
        
    def drawing_coords(self, num_of_points_per_seg=20):
        """Return the coordinates sequence that used by PIL to approximately
           draw this path."""
        coords = [(self.start.x, self.start.y)]
        for seg in self.segments:
            coords.extend(seg.drawing_coords(num_of_points_per_seg)[1:])
        return coords
        
