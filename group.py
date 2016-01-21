'''
Created on Apr 13, 2010

@author: yaocheng
'''

class Group(object):
    '''A class representing a set of SVG elements.'''

    def __init__(self):
        '''Initialize an empty set for collecting elements.'''
        self.group = []
    
    def include(self, element):
        '''Include a new element into the group.'''
        self.group.append(element)
        
    def other_method(self):
        '''Some other methods for group, such as delete a element or combine with 
           another group.'''
        pass