
from PIL import Image
from PIL import ImageDraw

if __name__ == '__main__':
    
    img = Image.open('/Users/yaocheng/Desktop/ROI/s011_extended.png', 'r')
    draw = ImageDraw.Draw(img)
    # draw.rectangle([(314.940, 299.06), (2578.940, 1610.35)], outline=128)
    draw.rectangle([(388 * 1.25, 355 * 1.25), (1969 * 1.25, 1162 * 1.25)], outline=128)
    img.save('/Users/yaocheng/Desktop/ROI/s011_framed.png', 'PNG')
