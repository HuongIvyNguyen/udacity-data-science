import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict
import schema

filename = 'west_seattle_wa.osm'

#========================#
### Audit STREET TYPES ###
#========================#

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE) # Define regular expressions for grabing street type

expected = ["Mall", "Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Way", "Broadway", "Circle", "Mall", "South", "East", "North", "Point", "Row", "West"] # List of the street types we expect to see in the US

def audit_street_type(street_types, street_name):
    """Parse street type from name and if not in expected move to dictionary"""
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    """ Identify element tag as street name"""
    return (elem.attrib['k'] == "addr:street")

def audit_street(osmfile):
    """" Parse osm file for inconsistent street types"""
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib["v"])
    return street_types


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

def update_name(name, mapping =mapping):
    """Update the street type to the right format identified"""
        words = name.split(" ")
        for word in words:
            if word == key:
                words.remove(word)
                words.append(item)
        name = ' '.join(word for word in words)
    return name

def fixed_street_type(osmfile):
    """Apply the update_name function to the entire osm file of the dataset"""
    st_types = dict(audit_street(osmfile))
    for st_type, ways in st_types.items():
        for name in ways:
            better_name = update_name(name, mapping)
    print(better_name)


#============================#
### Audit TELEPHONE FORMAT ###
#============================#

def validNumber(phone_number):
    """Define regex for the right format telephone"""
    pattern = re.compile("^[\d]{3}-[\d]{3}-[\d]{4}$", re.IGNORECASE)
    return pattern.match(phone_number) 

def audit_phone_type(wrong_format, right_format, this_number):
    """Parse through the value and make a list of right format versus a list of wrong format telephone"""
    phone_number = validNumber(this_number)
    if phone_number is not None and this_number != 'NULL':
        phone_type = phone_number.group()
        right_format.add(phone_type)
    else:
        wrong_format.append(this_number)

def is_phone(element):
    """Identify element tag as phone number"""
    return ((element.attrib['k'] == "phone") or (element.attrib['k'] == "contact:phone"))

def audit_phone(osmfile):
    """" Parse osm file for inconsistent telephone format"""
    osm_file = open(filename, "r")  
    wrong_format = []
    right_format = set([])
    
    for event, element in ET.iterparse(osmfile, events=('start',)):
        if element.tag == 'node' or element.tag == 'way':
            for tag in element.iter('tag'):
                if is_phone(tag):
                    audit_phone_type(wrong_format, right_format, tag.attrib['v'])
    return wrong_format, right_format

unexpected = [' ','+','-','\u2002','(',')',';','.','=','.','x','–','?'] #Define a list of expected characters in telephone for the wrong format list
        
def update_phone_format(osmfile):
    """Correct all wrong format telephones to the right format xxx-xxx-xxxx"""
    wrong_format, right_format = audit_phone(osmfile)
    fixed_phone_format = []
    for phone_number in wrong_format:
        for char in phone_number:
            if char in unexpected:
                phone_number = phone_number.replace(char,'')
        if phone_number.isdigit() == False or len(phone_number) < 10:
            phone_number = 'NULL'
            fixed_phone_format.append(phone_number)
        elif phone_number.isdigit() and len(phone_number) == 10:
            phone_number = phone_number[:3]+'-'+phone_number[3:6]+'-'+phone_number[6:10]
            fixed_phone_format.append(phone_number)
        elif phone_number.isdigit() and len(phone_number) == 11:
            phone_number = phone_number[1:4]+'-'+phone_number[4:7]+'-'+phone_number[7:11]
            fixed_phone_format.append(phone_number)
        elif 11 < len(phone_number) < 19:
            phone_number = phone_number[1:12]
            phone_number = phone_number[:3]+'-'+phone_number[3:6]+'-'+phone_number[6:10]
            fixed_phone_format.append(phone_number)
        else:
            phone_number = phone_number[:11]
            phone_number = phone_number[:3]+'-'+phone_number[3:6]+'-'+phone_number[6:10]
            fixed_phone_format.append(phone_number)
        return (fixed_phone_format+right_format)
            

#===========================#
### Audit POSTCODE FORMAT ###
#===========================#

def audit_postcode_type(error_codes, postcodes, checking):
     """Parse through the value and make a list of right format versus a list of wrong format postcodes"""
    if checking.isdigit() == False:
        error_codes.append(checking)
    elif len(checking) != 5:
        error_codes.append(checking)
    else:
        postcodes.add(checking)
        
def is_postcode(element):
    return (element.attrib['k'] == 'addr:postcode')

def audit_postcode(osmfile):
    """Identify element tag as postcode"""
    osmfile = open(osmfile, 'r')
    postcodes = set([])
    error_codes = []
    
    for event, element in ET.iterparse(osmfile, events=('start',)):
        if element.tag == 'node' or element.tag == 'way':
            for tag in element.iter('tag'):
                if is_postcode(tag):
                    audit_postcode_type(error_codes, postcodes, tag.attrib['v'])
    return error_codes, postcodes


def fix_postcodes(filename):
    "Fix postcodes with wrong format to the right format"
    error_codes, postcodes = audit_postcode(filename)
    for postcode in error_codes:
        postcode = postcode[:5]      
    return postcode 
