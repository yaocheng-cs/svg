'''
Created on May 20, 2010

@author: yaocheng
'''

from SVG import *

if __name__ == '__main__':
    svg = SVG.open('/Users/yaocheng/Desktop/ROI/ARA-Sagittal-011.svg')
    svg.load()
    svg.collect2('path', 'd')
    svg.collect2('text', 'transform')
    
    fp = open('/Users/yaocheng/Desktop/ROI/s011_path', 'w')
    for i in svg.data['path']:
        fp.write(i + '\n')
    fp.close()
    
    fp = open('/Users/yaocheng/Desktop/ROI/s011_text', 'w')
    for i in svg.data['text']:
        fp.write(i + '\n')
    fp.close()
    