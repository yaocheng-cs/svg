'''
Created on May 21, 2010

@author: yaocheng
'''

import re

from PIL import Image
from PIL import ImageDraw

from SVG import *
from basic import *
from path import *

#if __name__ == '__main__':
term_name_pos = []
fp = open('/Users/yaocheng/Desktop/ROI/s010_text', 'r')
for line in fp.readlines():
    m, t = line.strip('\n').split('   ')
    m = m.strip('matrix()').split()
    m = [float(n) for n in m]
    x = m[4] * 1.25
    y = m[5] * 1.25
    term_name_pos.append((t, x, y))

fp = open('/Users/yaocheng/Desktop/ROI/s010_roi_term', 'w')
buf = ''
#img = Image.new('RGB', (2880, 1800), 'white')
#draw = ImageDraw.Draw(img)

seg_ptn = re.compile('[MmLlHhVvCcSsQqTtAaZz][-0-9\., ]*')
num_ptn = re.compile('(?:[-,]?[0-9]+(?:\.[0-9]+)?)')

for i in range(1, 121):
    print i
    svg = SVG.open('/Users/yaocheng/Desktop/ROI/s010/' + str(i) + '.svg')
    svg.load()
    svg.collect('path', 'd')
    
    path = svg.data['path'][0]
    segs = seg_ptn.findall(path)
    cursor = None
    
    paths = []
    for seg in segs:
        cmd = seg[0]
        if cmd in ['Z', 'z']:
            path.close()
            cursor = path.start
        else:
            nums = num_ptn.findall(seg.strip(' MmLlHhVvCcSsQqTtAaZz'))
            nums = [float(n.strip(',')) for n in nums]
            if cmd in 'Mm':
                path = Path()
                paths.append(path)
                while len(nums) > 0:
                    x = nums.pop(0)
                    y = nums.pop(0)
                    if cmd == 'M':
                        x = x * 1.25
                        y = (-y + 1440) * 1.25
                    else:
                        if not cursor: # 'm' appear as the first element of a path
                            x = x * 1.25
                            y = (-y + 1440) * 1.25
                        else:
                            x = cursor.x + x * 1.25
                            y = cursor.y + y * -1.25
                    p = Point(x, y)
                    if not path.start:
                        path.start = p
                    else:
                        sl = StraightLine.from_points(cursor, p)
                        path.extend(sl)
                    path.end = p
                    cursor = p
            if cmd in 'Ll':
                while len(nums) > 0:
                    x = nums.pop(0)
                    y = nums.pop(0)
                    if cmd == 'L':
                        x = x * 1.25
                        y = (-y + 1440) * 1.25
                    else:
                        x = cursor.x + x * 1.25
                        y = cursor.y + y * -1.25
                    p = Point(x, y)
                    sl = StraightLine.from_points(cursor, p)
                    path.extend(sl)
                    path.end = p
                    cursor = p
            if cmd in 'Cc':
                while len(nums) > 0:
                    c1_x = nums.pop(0)
                    c1_y = nums.pop(0)
                    c2_x = nums.pop(0)
                    c2_y = nums.pop(0)
                    a2_x = nums.pop(0)
                    a2_y = nums.pop(0)
                    if cmd == 'C':
                        c1_x = c1_x * 1.25
                        c1_y = (-c1_y + 1440) * 1.25
                        c2_x = c2_x * 1.25
                        c2_y = (-c2_y + 1440) * 1.25
                        a2_x = a2_x * 1.25
                        a2_y = (-a2_y + 1440) * 1.25
                    else:
                        c1_x = cursor.x + c1_x * 1.25
                        c1_y = cursor.y + c1_y * -1.25
                        c2_x = cursor.x + c2_x * 1.25
                        c2_y = cursor.y + c2_y * -1.25
                        a2_x = cursor.x + a2_x * 1.25
                        a2_y = cursor.y + a2_y * -1.25
                    c1 = Point(c1_x, c1_y)
                    c2 = Point(c2_x, c2_y)
                    a2 = Point(a2_x, a2_y)
                    cb = CubicBezier(cursor, c1, c2, a2)
                    path.extend(cb)
                    path.end = a2
                    cursor = a2
                    
    for p in paths:
        dc = p.drawing_coords()
        #draw.line(dc, fill=128, width=1)
        sum_x = 0
        sum_y = 0
        for pair in dc:
            sum_x += pair[0]
            sum_y += pair[1]
        center_x = sum_x / len(dc)
        center_y = sum_y / len(dc)
        
        segs = ''
        for s in p.segments:
            if segs == '':
                if isinstance(s, StraightLine):
                    segs = segs + str(s.a1.x - center_x) + ',' + str(s.a1.y - center_y) + ' ' + str(s.a2.x - center_x) + ',' + str(s.a2.y - center_y)
                if isinstance(s, QuadraticBezier):
                    segs = segs + str(s.a1.x - center_x) + ',' + str(s.a1.y - center_y) + ' ' + str(s.c.x - center_x) + ',' + str(s.c.y - center_y) + ' ' + str(s.a2.x - center_x) + ',' + str(s.a2.y - center_y)
                if isinstance(s, CubicBezier):
                    segs = segs + str(s.a1.x - center_x) + ',' + str(s.a1.y - center_y) + ' ' + str(s.c1.x - center_x) + ',' + str(s.c1.y - center_y) + ' ' + str(s.c2.x - center_x) + ',' + str(s.c2.y - center_y) + ' ' + str(s.a2.x - center_x) + ',' + str(s.a2.y - center_y)
            else:
                if isinstance(s, StraightLine):
                    segs = segs + str(s.a2.x - center_x) + ',' + str(s.a2.y - center_y)
                if isinstance(s, QuadraticBezier):
                    segs = segs + str(s.c.x - center_x) + ',' + str(s.c.y - center_y) + ' ' + str(s.a2.x - center_x) + ',' + str(s.a2.y - center_y)
                if isinstance(s, CubicBezier):
                    segs = segs + str(s.c1.x - center_x) + ',' + str(s.c1.y - center_y) + ' ' + str(s.c2.x - center_x) + ',' + str(s.c2.y - center_y) + ' ' + str(s.a2.x - center_x) + ',' + str(s.a2.y - center_y)
            segs = segs + ';'
        
        ts = []
        for t in term_name_pos: 
            flag = False
            for i in range(0, len(dc) - 1):
                if dc[i][1] < t[2] and dc[i+1][1] > t[2] or \
                dc[i][1] > t[2] and dc[i+1][1] < t[2]:
                    sl = StraightLine.from_points(Point(dc[i][0], dc[i][1]), \
                                                  Point(dc[i+1][0], dc[i+1][1]))
                    if t[1] > sl.get_x_from_y(t[2]):
                        flag = not flag
            if flag:
                ts.append(t[0])
    
        buf = buf + segs.strip(';') + '   ' + str(ts) + '   ' + str(center_x) + ',' + str(center_y) + '\n'
    
fp.write(buf.strip('\n'))
fp.close()
#img.save('/Users/yaocheng/Desktop/ROI/test_s010_redraw.png', 'PNG')