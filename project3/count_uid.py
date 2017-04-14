import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict

filename = 'west_seattle_wa.osm'

def process_users(filename):
    """Counting number of contributors to the dataset"""
    users = set()
    for event, element in ET.iterparse(filename):
        if 'uid' in element.attrib:
            users.add(element.get('uid'))
    return users


print(len(process_users(filename)))