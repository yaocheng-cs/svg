'''
Created on Apr 17, 2010

@author: yaocheng
'''

import re

from PIL import Image
from PIL import ImageDraw

from basic import *
from path import *
from group import *
from utils import *

if __name__ == '__main__':
    
    # fp = open('C:\\Users\\Yao\\Desktop\\svgPy\\path.txt', 'r')
    fp = open('/Users/yaocheng/Desktop/ROI/s011_path', 'r')
    group = Group()
    pattern = re.compile('(?:[-,]?[0-9]+(?:\.[0-9]+)?)')
    
    for line in fp.readlines():
        path = None
        cursor = Point(0, 0) # can't initialize to None because of command "moveto"
        
        for seg in line.split():
            command = seg[0]
            if command in 'Zz':
                path.close()
            else:
                '''Get and convert to actual coordinate(number) from a command 
                   section'''
                nums = pattern.findall(seg[1:])
                for i in range(0, len(nums)):
                    nums[i] = float(nums[i].strip(',')) * 1.25 # 1.25 is just a size factor
                        
                '''Convert relative coordinate to abstract coordinate
                   Ignore Arc(a) for now'''
                if command in 'mlcsqt':
                    for i in range(0, len(nums)):
                        if i % 2 == 0:
                            nums[i] = nums[i] + cursor.x
                        else:
                            nums[i] = nums[i] + cursor.y
                elif command == 'h':
                    nums[0] = nums[0] + cursor.x
                elif command == 'v':
                    nums[0] = nums[0] + cursor.y
                    
                '''Decide how to proceed with current path
                   Ignore Quadratic Bezier and Arc for now'''
                if command in 'Mm':
                    current_seg = None
                    if not path:
                        path = Path()
                    p1 = Point(nums[0], nums[1])
                    cursor = p1
                else:
                    previous_seg = current_seg
                    if command in 'LlHhVv':
                        if command in 'Ll':
                            p1 = Point(nums[0], nums[1])  
                        if command in 'Hh':
                            p1 = Point(nums[0], cursor.y)
                        if command in 'Vv':
                            p1 = Point(cursor.x, nums[0])
                        current_seg = StraightLine.from_points(cursor, p1)
                        cursor = p1
                    elif command in 'CcSs':
                        p1 = Point(nums[0], nums[1])
                        p2 = Point(nums[2], nums[3])
                        if command in 'Cc':
                            p3 = Point(nums[4], nums[5])
                            current_seg = CubicBezier(cursor, p1, p2, p3)
                            cursor = p3
                        if command in 'Ss':
                            if isinstance(previous_seg, CubicBezier):
                                mirror = Point(2 * cursor.x - previous_seg.c2.x, 2 * cursor.y - previous_seg.c2.y)
                            else:
                                mirror = cursor.clone()
                            current_seg = CubicBezier(cursor, mirror, p1, p2)
                            cursor = p2
                    else:
                        pass
                    path.extend(current_seg)
                    
        '''This is important, since there are empty paths (contain only a 
           "move" command but nothing else) in the input data'''
        if len(path.segments) > 0:            
            group.include(path)
            
    fp.close()
    
    queue = []
    queue.extend(group.group)
    
    while len(queue) > 0:
        current = queue.pop(0)
        if not current.closed:
            point_start = None
            distance_start = sys.maxint
            point_end = None
            distance_end = sys.maxint
            for path in group.group:
                if path is current:
                    continue
                ps, ds = Distance.point_to_path(current.start, path)
                if 0 < ds < distance_start: # not very natural to require ds > something
                    distance_start = ds
                    point_start = ps
                pe, de = Distance.point_to_path(current.end, path)
                if 0 < de < distance_end: # not very natural to require de > something
                    distance_end = de
                    point_end = pe
            if distance_start < 15:
                new_start_seg = StraightLine.from_points(point_start, current.start)
                new_start_seg.get_approx_points(20)
                current.unshift(new_start_seg)
            if distance_end < 15:
                new_end_seg = StraightLine.from_points(current.end, point_end)
                new_end_seg.get_approx_points(20)
                current.extend(new_end_seg)
                
    # img = Image.new('RGB', (5940, 4320), 'white')
    img = Image.new('RGB', (2880, 1800), 'white')
    draw = ImageDraw.Draw(img)
    for path in group.group:
        draw.line(path.drawing_coords(), fill=128, width=1)
    img.save('/Users/yaocheng/Desktop/ROI/s011_extended.png', 'PNG')
