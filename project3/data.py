#!/usr/bin/env python
# -*- coding: utf-8 -*-



import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schema

OSM_PATH = "sample_west_seattle.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE) # Define regular expressions for grabing street type

expected = ["Mall", "Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Way", "Broadway", "Circle", "Mall", "South", "East", "North", "Point", "Row", "West"] 

mapping = {'Ave' : 'Avenue',
          'E' : 'East',
          'N' : 'North', 
          'Pl' : 'Place',
          'S' : 'South',
          'SW' : 'Southwest',
          'St' : 'Street',
          'St.' : 'Street',
           'driveway' : 'Driveway'
          }


def fix_street_type(value, mapping=mapping):
    m = street_type_re.search(value)
    if m:
        street_type = m.group()
        if street_type not in expected:
            words = value.split(" ")
            for key, item in mapping.items():    
                for word in words:
                    if word == key:
                        word = item
                    name = ' '.join(word for word in words)
    return name

phone_format_re = re.compile("^[\d]{3}-[\d]{3}-[\d]{4}$", re.IGNORECASE)
unexpected = [' ','+','-','\u2002','(',')',';','.','=','.','x','–','?']

def fix_phone_format(phone_number, phone_format_re=phone_format_re, unexpected=unexpected):
    if phone_format_re.match(phone_number) is None:
        for char in phone_number:
            if char in unexpected:
                phone_number = phone_number.replace(char,'')
        if phone_number.isdigit() == False or len(phone_number) < 10:
            phone_number = 'NULL'
        elif phone_number.isdigit() and len(phone_number) == 10:
            phone_number = phone_number[:3]+'-'+phone_number[3:6]+'-'+phone_number[6:10]
        elif phone_number.isdigit() and len(phone_number) == 11:
            phone_number = phone_number[1:4]+'-'+phone_number[4:7]+'-'+phone_number[7:11]
        elif 11 < len(phone_number) < 19:
            phone_number = phone_number[1:12]
            phone_number = phone_number[:3]+'-'+phone_number[3:6]+'-'+phone_number[6:10]
        else:
            phone_number = phone_number[:11]
            phone_number = phone_number[:3]+'-'+phone_number[3:6]+'-'+phone_number[6:10]
    return phone_number

def fix_postcode(postcode):
    if postcode.isdigit() == False:
        postcode = postcode[:5]
    elif len(postcode) != 5:
        postcode = postcode[:5]
    return postcode


def fix_attribute(value):
    new_value = None
    if value.attrib['k'] == 'addr:str':
        new_value = fix_street_type(value.attrib['v'])
    elif value.attrib['k'] == 'phone' or value.attrib['k'] == 'contact:phone':
        new_value = fix_phone_format(value.attrib['v'])
    elif value.attrib['k'] == 'addr:postcode':
        new_value = fix_postcode(value.attrib['v'])
    else:
        new_value = value.attrib['v']
    return new_value
    
def made_node(element, node_attribs, tags):
    for attrib in element.attrib:
        if attrib in NODE_FIELDS:
            node_attribs[attrib] = element.attrib[attrib]
    
    for child in element:
        node_tag = {}
        if LOWER_COLON.match(child.attrib['k']):
            node_tag['type'] = child.attrib['k'].split(':',1)[0]
            node_tag['key'] = child.attrib['k'].split(':',1)[1]
            node_tag['id'] = element.attrib['id']
            node_tag['value'] = fix_attribute(child)
            tags.append(node_tag)
        elif PROBLEMCHARS.match(child.attrib['k']):
            continue
        else:
            node_tag['type'] = 'regular'
            node_tag['key'] = child.attrib['k']
            node_tag['id'] = element.attrib['id']
            node_tag['value'] = fix_attribute(child)
            tags.append(node_tag)
    return  node_attribs, tags

def made_way(element, way_attribs, way_nodes, tags):
    for attrib in element.attrib:
        if attrib in WAY_FIELDS:
            way_attribs[attrib] = element.attrib[attrib]
            
    position = 0
    for child in element:
        way_tag = {}
        way_node = {}
        
        if child.tag == 'tag':
            if LOWER_COLON.match(child.attrib['k']):
                way_tag['type'] = child.attrib['k'].split(':',1)[0]
                way_tag['key'] = child.attrib['k'].split(':',1)[1]
                way_tag['id'] = element.attrib['id']
                way_tag['value'] = fix_attribute(child)
                tags.append(way_tag)
            elif PROBLEMCHARS.match(child.attrib['k']):
                continue
            else:
                way_tag['type'] = 'regular'
                way_tag['key'] = child.attrib['k']
                way_tag['id'] = element.attrib['id']
                way_tag['value'] = fix_attribute(child)
                tags.append(way_tag)
                
        elif child.tag == 'nd':
            way_node['id'] = element.attrib['id']
            way_node['node_id'] = child.attrib['ref']
            way_node['position'] = position
            position += 1
            way_nodes.append(way_node)
    return way_attribs, way_nodes, tags


def shape_element(element):
    """Clean and shape node or way XML element to Python dict"""
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  
    

    if element.tag == 'node':
        node_attribs, tags = made_node(element, node_attribs, tags)
        return {'node': node_attribs, 'node_tags' : tags}
    elif element.tag == 'way':
        way_attribs, way_nodes, way_tags = made_way(element, way_attribs, way_nodes, tags)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}

    
# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v,unicode) else v) for k, v in row.items()
        })

    def writerows(self, rows):  
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

if __name__ == '__main__':
    process_map(OSM_PATH, validate=True)

