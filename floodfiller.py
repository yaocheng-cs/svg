'''
Created on Apr 18, 2010

@author: yaocheng
'''

from PIL import Image
from PIL import ImageDraw

class FloodFill(object):
    
    def __init__(self):
        pass
        
    def west(self):
        return (self.current[0] - 1, self.current[1])
    
    def east(self):
        return (self.current[0] + 1, self.current[1])
    
    def north(self):
        return (self.current[0], self.current[1] - 1)
    
    def south(self):
        return (self.current[0], self.current[1] + 1)
        
    def set_img(self, img):
        self.size = img.size
        self.pix = img.load()

    def set_fill(self, seed, target, replacement):
        self.seed = seed
        self.target = target
        self.replacement = replacement
        
    def run(self):
        self.current = self.seed
        if self.pix[self.current] != self.target:
            return None
        queue = [self.current]
        inside = []
        boundary = []
        while len(queue) > 0:
            self.current = queue.pop(0)
            self.pix[self.current] = self.replacement
            inside.append(self.current)
            for pos in [self.west(), self.east(), self.north(), self.south()]:
                if pos[0] < 0 or pos[0] >= self.size[0] or \
                   pos[1] < 0 or pos[1] >= self.size[1]:
                    continue
                if self.pix[pos] == self.target:
                    self.pix[pos] = self.replacement
                    queue.append(pos)
                else:
                    if self.pix[pos] != self.replacement:
                        boundary.append(pos)
        inside.extend(boundary)
        return inside

        
if __name__ == '__main__':    
    img = Image.open('/Users/yaocheng/Desktop/ROI/s011_framed.png', 'r')
    f = FloodFill()
    f.set_img(img)
    
    '''The first seed should be just inside the frame
       The coordinate depends on how the frame is drawed'''
    x = 388 * 1.25 + 1
    y = 355 * 1.25 + 1
    
    target = (255, 255, 255)
    repl_pool_backup = [(139, 136, 120), (255, 255, 0), (255, 0, 0), 
                        (255, 0, 255), (0, 255, 0), (0, 0, 255), (0, 0, 0), 
                        (0, 255, 255)]
    repl_pool = []
    repl_pool.extend(repl_pool_backup)
    replacement = repl_pool.pop(0)
    j = 0
    while y <= 1162 * 1.25 - 1:
        while x <= 1969 * 1.25 - 1:
            f.set_fill((x, y), target, replacement)
            area = f.run()
            if not area:
                x += 10
                continue
            else:
                i = Image.new('RGB', (2880, 1800), 'white')
                draw = ImageDraw.Draw(i)
                draw.point(area, fill=0)
                i = i.convert('1')
                path = '/Users/yaocheng/Desktop/ROI/s011/' + str(j) + '.bmp'
                i.save(path, 'BMP')
                j += 1
                if len(repl_pool) < 1:
                    repl_pool.extend(repl_pool_backup)
                replacement = repl_pool.pop(0)
            x += 10
        y += 10
        x = 388 * 1.25 + 1
    img.save('/Users/yaocheng/Desktop/ROI/s011_filled.png')
