import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict

filename = 'west_seattle_wa.osm'

def count_tags(filename):
    """Make a dictionary of all tags with its corresponding count"""
    tags={}
    for event, elem in ET.iterparse(filename):
        tag = elem.tag
        if tag in tags:
            tags[tag] += 1
        else:
            tags[tag] = 1
    return tags

print(count_tags(filename))