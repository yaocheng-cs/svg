'''
Created on Jul 12, 2010

@author: yaocheng
'''

import re
import os
import time

from PIL import Image
from PIL import ImageDraw

from SVG import SVG
from basic import *
from path import Path
from utils import Distance
from floodfiller import FloodFill

def get_paths(filename):
    """Get a colletion of Path objects from text data."""
    pattern = re.compile('(?:[-,]?[0-9]+(?:\.[0-9]+)?)')
    paths = []
    
    fp = open(filename, 'r')
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
            paths.append(path)
            
    fp.close()
    return paths

def extend_paths(paths):
    """Given a collection of Path objects, extend each path's loose end if there is any."""
    queue = []
    queue.extend(paths)
    
    while len(queue) > 0:
        current = queue.pop(0)
        if not current.closed:
            point_start = None
            distance_start = sys.maxint
            point_end = None
            distance_end = sys.maxint
            for path in paths:
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
                
def redraw_paths(paths, frame=False):
    """Redraw the given collection of Paths in a new bitmap using PIL, adding 
       a rectangle frame into the bitmap as well."""
    top = 1440
    #top = 1800
    bottom = 0
    left = 1980
    #left = 2880
    right = 0
    
    img = Image.new('RGB', (1980, 1440), 'white')
    #img = Image.new('RGB', (2880, 1800), 'white')
    draw = ImageDraw.Draw(img)
    for path in paths:
        coords = path.drawing_coords()
        for p in coords:
            if p[0] < left:
                left = p[0]
            if p[0] > right:
                right = p[0]
            if p[1] < top:
                top = p[1]
            if p[1] > bottom:
                bottom = p[1]
        draw.line(coords, fill=128, width=1)
    if frame:    
        draw.rectangle([(left - 2, top - 2), (right + 2, bottom + 2)], outline=128)
        img.save(section_name + '.png', 'PNG')
        return [(left, top), (right, bottom)]
    else:
        img.save(section_name + '.png', 'PNG')

def floodfill_image(section_name, range=None):
    """Run floodfill algorithm against an image. Put the output in a folder."""
    img = Image.open(section_name + '.png', 'r')
    f = FloodFill()
    f.set_img(img)
    
    '''If frame exists, first seed should be just inside the frame
       The coordinate depends on how the frame is drawn'''
    if range is None:
        left = 2
        top = 2
        right = 1980 - 2 #right = 2880 - 2
        bottom = 1440 - 2 #bottom = 1800 - 2 
    else:    
        left = range[0][0]
        top = range[0][1]
        right = range[1][0]
        bottom = range[1][1]
    
    x = left
    y = top
    
    target = (255, 255, 255)
    repl_pool_backup = [(139, 136, 120), (255, 255, 0), (255, 0, 0), 
                        (255, 0, 255), (0, 255, 0), (0, 0, 255), (0, 0, 0), 
                        (0, 255, 255)]
    repl_pool = []
    repl_pool.extend(repl_pool_backup)
    replacement = repl_pool.pop(0)
    j = 0
    while y <= bottom:
        while x <= right:
            f.set_fill((x, y), target, replacement)
            area = f.run()
            if not area:
                x += 10
                continue
            else:
                i = Image.new('RGB', (1980, 1440), 'white')
                #i = Image.new('RGB', (2880, 1800), 'white')
                draw = ImageDraw.Draw(i)
                draw.point(area, fill=0)
                i = i.convert('1')
                path = section_name + '/' + str(j) + '.bmp'
                i.save(path, 'BMP')
                j += 1
                if len(repl_pool) < 1:
                    repl_pool.extend(repl_pool_backup)
                replacement = repl_pool.pop(0)
            x += 10
        y += 10
        x = left
    img.save(section_name + '-color.png')

if __name__ == '__main__':
    print time.ctime()
    
    ROOT_PATH = '/Users/yaocheng/Desktop/Active/test/'
    FILE_NAME_PREFIX = 'ARA-Coronal-'
    #SECTION_NUMS = ['000', '001', '002', '003', '004', '005', '006', '007', '008', '009', 
    #                '010', '011', '012', '013', '014', '015', '016', '017', '018', '019', 
    #                '020', '021']
    SECTION_NUMS = ['000',
                    '060', '061', '062', '063', '064', '065', '066', '067', '068', '069', 
                    '070', '071', '072', '073', '074', '075', '076', '077', '078', '079',
                    '080', '081', '082', '083', '084', '085', '086', '087', '088', '089', 
                    '090', '091', '092', '093', '094', '095', '096', '097', '098', '099',
                    '100', '101', '102', '103', '104', '105', '106', '107', '108', '109', 
                    '110', '111', '112', '113', '114', '115', '116', '117', '118', '119',
                    '120', '121', '122', '123', '124', '125', '126', '127', '128', '129', 
                    '130', '131', '132']
    
    for section_num in SECTION_NUMS[1:]:
        section_name = ROOT_PATH + FILE_NAME_PREFIX + section_num + 'BW'
        print section_name
        
        svg = SVG.open(section_name + '.svg')
        svg.load()
        svg.collect2('path', 'd')
        #svg.collect2('text', 'transform')
        
        fp = open(section_name + '-path', 'w')
        for i in svg.data['path']:
            fp.write(i + '\n')
        fp.close()
    
        #fp = open(section_name + '-text', 'w')
        #for i in svg.data['text']:
        #    fp.write(i + '\n')
        #fp.close()
        
        paths = get_paths(section_name + '-path')
        extend_paths(paths)
        redraw_paths(paths)
        os.mkdir(section_name)
        floodfill_image(section_name)
        
    print time.ctime()
    
        
        
        
        
        