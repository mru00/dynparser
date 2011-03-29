import re
import logging
from namespace import *

class TE(object):
    expression = re.compile(r"\w+")
    def __init__(self):
        self.value = None
        self.isparsed = False
    def dump(self, level=0):
        return "\n" + " "*level + self.__class__.__name__ + " value: " + str(self.value)
    def onparse(self):
        pass
    def postparse(self):
        if not self.isparsed:
            self.onparse()
            self.isparsed = True
    def canparse(self):
        return True

class NTE(object):
    def __init__(self):
        self.items = []
        self.isparsed = False
    def add(self, item):
        self.items.append(item)
    def get_first(self, clazz):
        return self.get_items(clazz)[0]
    def get_items(self, clazz):
        logging.debug("+searching for %s" % str(clazz))
        for i in self.items:
            logging.debug("  could be %s" % i)
        l = filter(lambda a: isinstance(a,eval(clazz)),  self.items)
        for i in l:
            logging.debug("  is %s" % i)

        return l
    def postparse(self):
        if not self.isparsed:
            self.onparse()
            self.isparsed = True
    def dump(self, level=0):
        d =  "\n"+ " "*level + self.__class__.__name__
        for i in self.items:
            d += i.dump(level+1)
        return d
    def onparse(self):
        pass
    def canparse(self):
        return True


