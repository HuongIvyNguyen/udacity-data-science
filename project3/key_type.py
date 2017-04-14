                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict

filename = 'west_seattle_wa.osm'

# "lower", for tags that contain only lowercase letters and are valid,
# "lower_colon", for otherwise valid tags with a colon in their names,
# "problemchars", for tags with problematic characters, and
# "other", for other tags that do not fall into the other three categories.

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
    """Make a dictionary of all keys with their corresponding count"""
    if element.tag == "tag":
        value = element.get('k')
        if lower.search(value):
            keys['lower'] +=1
        elif lower_colon.search(value):
            keys['lower_colon'] +=1
        elif problemchars.search(value):
            keys['problemchars'] +=1
        else:
            keys['other'] +=1
    return keys



def process_map(filename):
    """Apply the key_type function to the given osm dataset"""
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys

print(process_map(filename))