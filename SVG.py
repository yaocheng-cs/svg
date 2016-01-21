'''
Created on May 20, 2010

@author: yaocheng
'''

from lxml import etree

class SVG(object):
    """Class used to handle basic input (and output) functionalities. 
       Also, collect data of interest from a SVG file."""
       
    NAMESPACE = '{http://www.w3.org/2000/svg}'

    def __init__(self):
        """Initialize a dictionary to be the container of interested data."""
        self.data = {}
    
    @classmethod    
    def open(cls, file_path):
        """Open an SVG file."""
        svg = SVG()
        svg.fp = open(file_path, 'r')
        return svg
        
    def load(self):
        """Load data from the opened file, use lxml to parse the data."""
        tree = etree.parse(self.fp)
        self.root = tree.getroot()
        self.fp.close()
        
    def close(self):
        """Close the svg file pointer."""
        if self.fp:
            self.fp.close()
            
    def collect(self, tag, attribute):
        """Given a tag name and an attribute name (or just "text"), collect the 
           attribute value (or text content), from elements of that tag."""
        values = []
        for element in self.root.iter(self.NAMESPACE + tag):
            if attribute in ['TEXT', 'text', 'Text']:
                value = element.text
            else:
                value = element.get(attribute)
            values.append(value)
        self.data[tag] = values
        
    def collect2(self, tag, attribute):
        """A special edition of the collect method."""
        values = []
        for element in self.root.iter(self.NAMESPACE + tag):
            value = element.get(attribute)
            if tag is 'path':
                
                # A special escape from some unwanted path data in some of the coronal sections
                if value == 'M-6.5-5V5l13-5.004L-6.5-5z':
                    continue
                
                value = value.replace(' ', '')
                for cmd in ['Z', 'z']:
                    value = value.replace(cmd, cmd + '\n')
                value = value.strip('\n')
                for cmd in ['L', 'l', 'H', 'h', 'V', 'v', 'C', 'c', 'S', 's', 
                            'Q', 'q', 'T', 't', 'A', 'a', 'Z', 'z']:
                    value = value.replace(cmd, ' ' + cmd)
                values.extend(value.split('\n'))
            if tag is 'text':
                if element.text is not None:
                    value = value + '   ' + element.text.strip()
                    values.append(value)
        self.data[tag] = values
            
        
        
