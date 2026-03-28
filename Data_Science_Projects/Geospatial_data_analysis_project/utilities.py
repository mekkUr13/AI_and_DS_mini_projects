import ast
import json
import os
import random
import webbrowser

import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.simpledialog
import math

import folium
import pyproj

# A small epsilon for float comparisons
EPSILON = 1e-9

folium_colours = [
    'red', 'blue', 'green', 'purple', 'orange', 
    'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen',
    'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue',
    'lightgreen', 'gray', 'black', 'lightgray'
]

geoformats = {
    'csv': ('CSV Files', '*.csv'),
    'geojson': ('GeoJSON Files', '*.geojson'),
    'shp': ('Shapefiles', '*.shp'),
    'png': ('PNG Files', '*.png')
}


def warning(message, title='Warning'):

    tkinter.Tk().withdraw()
    tkinter.messagebox.showwarning(title, message)


def error(message, title='Error'):

    tkinter.Tk().withdraw()
    tkinter.messagebox.showerror(title, message)


def input_file(formats=None, title='Select input file'):
    """Open a dialogue box to select an existing file"""

    try:

        if formats is None:
            filetypes = [('All Files', '*.*')]
        else:
            filetypes = []

            for geoformat in formats:

                try:
                    filetypes.append(geoformats[geoformat.lower()])
                except:
                    continue

                filetypes.append(('All Files', '*.*'))

        # GUI

        tkinter.Tk().withdraw()

        filename = tkinter.filedialog.askopenfilename(
            title=title, filetypes=filetypes
        )

        if not filename:
            filename = None
    except:
        filename = None

    return filename


def output_file(formats=None, title='Select output file'):
    """Open a dialogue box to select a new output file"""

    try:

        if formats is None:
            filetypes = [('All Files', '*.*')]
        else:
            filetypes = []

            for geoformat in formats:

                try:
                    filetypes.append(geoformats[geoformat.lower()])
                except:
                    continue

                filetypes.append(('All Files', '*.*'))

        # GUI

        tkinter.Tk().withdraw()

        filename = tkinter.filedialog.asksaveasfilename(
            title=title, filetypes=filetypes
        )

        if not filename:
            filename = None
    except:
        filename = None

    return filename




def random_points(n, x_min, y_min, x_max, y_max):

    # TODO: check x_max > x_min and y_max > y_min

    delta_x = x_max - x_min
    delta_y = y_max - y_min

    coordinates = []
    attributes = []

    for count in range(n):

        x_random = x_min + random.random() * delta_x
        y_random = y_min + random.random() * delta_y

        coordinates.append([x_random, y_random])

        attributes.append({'id': count})

    return [coordinates, attributes]

    

def create_osm_layer(vector):

    # Folium layer
    osm_layer = folium.FeatureGroup(name='osm')

    # Default colour and size/width
    colour = 'blue'
    size = 10 # points
    width = 1 # polylines/polygons

    # Colour and size

    if 'colour' in vector.fields:
        colour = vector.attributes[count]['colour']
    elif 'color' in vector.fields:
        colour = vector.attributes[count]['color']

    if colour not in folium_colours:
        colour = 'blue'

    if 'size' in vector.fields:
        size = vector.attributes[count]['size']

    # Scan dataset
    if vector._geometry == 'POINT':
        for count, point in enumerate(vector.coordinates):
            # Coordinates
            longitude, latitude = point

            # Popup
            osm_popup_text = '' # HTML code

            for field, value in vector._attributes[count].items():
                osm_popup_text += f'{field.upper()}: {value}<br>'

            osm_popup = folium.Popup(osm_popup_text, max_width=500)
            
            # Marker
            osm_marker = folium.CircleMarker(
                location=[latitude, longitude],
                popup=osm_popup,
                radius=size,
                color=colour,
                fill=True,
                fill_color=colour,
                fill_opacity=0.4
            )

            osm_layer.add_child(osm_marker)
    elif vector._geometry == 'POLYLINE':
        pass
    elif vector._geometry == 'POLYGON':
        for count, polygon in enumerate(vector.coordinates):
            # Coordinates
            folium_polygon = []
            for point in polygon[0]:
                longitude, latitude = point
                folium_polygon.append([latitude, longitude])

            # Popup
            osm_popup_text = '' # HTML code

            for field, value in vector._attributes[count].items():
                osm_popup_text += f'{field.upper()}: {value}<br>'

            osm_popup = folium.Popup(osm_popup_text, max_width=500)
            
            # Polygon
            osm_polygon = folium.Polygon(
                locations=folium_polygon,
                popup=osm_popup,
                weight=width,
                color=colour,
                fill=True,
                fill_color=colour,
                fill_opacity=0.4
            )

            osm_layer.add_child(osm_polygon)

    return osm_layer


def draw_osm_map(layers):

    # layers is a list of osm_layers

    osm_map = folium.Map()

    for layer in layers:
        osm_map.add_child(layer)

    osm_map.fit_bounds(
        osm_map.get_bounds()
    )

    filename = 'osm.html'
    
    osm_map.save(filename)

    webbrowser.open(
        os.path.abspath(filename)
    )


def validate(expression):
    """Validate an expression to be processed with eval()"""
    
    validation = {'status': True, 'tokens': []}

    block_list = ['os']

    # Get syntax tree

    try:
        tree = ast.parse(expression, mode='eval')
    except:
        validation['status'] = False
        validation['message'] = f'Syntax error in expression "{expression}"'
        return validation

    # Get relevant tokens

    module = []
    function = []
    arithmetic = []
    logical = []
    relational = []
    constant = []
    label = [] # Field names

    for node in ast.walk(tree):

        class_name = node.__class__.__name__

        if class_name == 'Call':
            try:
                function.append(node.func.id) # simple function
            except:
                module.append(node.func.value.id)
                function.append(f'{node.func.value.id}.{node.func.attr}')
        elif class_name in ['Add', 'Sub', 'Mult', 'Div', 'Pow']:
            arithmetic.append(class_name)
        elif class_name in ['Not', 'And', 'Or']:
            logical.append(class_name)
        elif class_name in ['Eq', 'NotEq', 'Gt', 'Lt', 'GtE', 'LtE']:
            relational.append(class_name)
        elif class_name == 'Constant':
            constant.append(node.value)
        elif hasattr(node, 'id'):
            if node.id not in function and node.id not in module:
                label.append(node.id)

    # Dictionary of tokens

    tokens = {
        'module': module,
        'function': function,
        'arithmetic': arithmetic,
        'logical': logical,
        'relational': relational,
        'constant': constant,
        'label': label
    }

    validation['tokens'] = tokens

    # Check block_list

    for token in tokens['module']:
        if token in block_list:
            validation['status'] = False
            validation['message'] = f'Forbidden keyword "{token}"'
            break

    return validation


def read_points_csv(filename, id_field, x_field, y_field, separator):

    # Read file
    with open(filename, 'rt') as csv_file:
        data = csv_file.readlines()

    # Check there is a header
    # TODO

    # Check fields exist
    header = data[0].strip().split(separator)

    if id_field not in header:
        error(f'ID field "{id_field}" nor found')
        return
    
    if x_field not in header:
        error(f'X coordinate field "{x_field}" nor found')
        return
    if y_field not in header:
        error(f'Y field "{y_field}" nor found')
        return

    # Field indices
    id_field_index = header.index(id_field)
    x_field_index = header.index(x_field)
    y_field_index = header.index(y_field)

    # Read data

    coordinates = []
    attributes = []

    for record in data[1:]:

        attribute = {}

        for field_index, field_value in enumerate(record.strip().split(separator)):

            if field_index == id_field_index:
                attribute['id'] = field_value
            elif field_index == x_field_index:
                x = float(field_value)
            elif field_index == y_field_index:
                y = float(field_value)
            else:
                attribute[header[field_index]] = field_value

        coordinates.append([x, y])
        attributes.append(attribute)

    return [coordinates, attributes]
                
    
def read_geojson(filename, geometry):

    try:
        with open(filename, 'rt') as geojson_file:
            data = json.load(geojson_file)
    except:
        return None

    # Process data
    coordinates = []
    attributes = []

    for count, feature in enumerate(data['features']):

        if feature['geometry']['type'] == geometry:
            # Coordinates
            coordinates.append(feature['geometry']['coordinates'])

            # Attributes
            record = {}
            record['id'] = count

            for field_name, field_value in feature['properties'].items():
                record[field_name] = field_value
                
            attributes.append(record)

    # EPSG
    epsg = 4326 # WGS 84. TODO: older versions

    return [coordinates, attributes, epsg]
    
    
def write_points_csv(vector, filename, world_epsg, world_file):
    """
    vector: instnace of vector() class
    filename: to store the output coordinates
    world_epsg: EPSG of the output coordinates
    world_file: transformation to output coordinates
    """
    

    # Header
    header = ['count', 'x', 'y'] + vector.fields

    with open(filename, 'wt') as csv_file:

        # Header record
        header_record = ','.join(header)

        csv_file.write(header_record + '\n')

        # Data records
        for count, point in enumerate(vector.coordinates):
            x, y = point

            if not world_file is None:
                x, y = screen_to_world(point, world_file)

            # TODO: dicuss World EPSG

            # Coordinates
            data_record = [count, x, y]

            # Attributes
            for field in vector.fields:
                data_record.append(vector.attributes[count][field])

            csv_file.write(','.join(map(str, data_record)) + '\n')
   

def screen_to_world(point, world_file):

    x, y = point

    a, d, b, e, c, f = world_file

    x_world = a * x + b * y + c
    y_world = d * x + e * y + f

    return [x_world, y_world]


def world_to_screen():
    pass

        
def read_world_file(filename):

    image_filename, image_extension = os.path.splitext(filename)

    world_extension = image_extension[1] + image_extension[-1] + 'w'

    world_filename = image_filename + '.' + world_extension

    try:
        with open(world_filename, 'rt') as world_file:
            records = world_file.readlines()

        world = list(map(float, records))

        if len(world) != 6:
            world = None
    except:
        world = None

    return world

def segment_intersection(seg1, seg2):
    p1, p2 = seg1
    p3, p4 = seg2

    denom = (p4[1] - p3[1]) * (p2[0] - p1[0]) - (p4[0] - p3[0]) * (p2[1] - p1[1])
    if denom == 0:
        return None

    ua = ((p4[0] - p3[0]) * (p1[1] - p3[1]) - (p4[1] - p3[1]) * (p1[0] - p3[0])) / denom
    ub = ((p2[0] - p1[0]) * (p1[1] - p3[1]) - (p2[1] - p1[1]) * (p1[0] - p3[0])) / denom

    if 0 < ua < 1 and 0 < ub < 1:
        x = p1[0] + ua * (p2[0] - p1[0])
        y = p1[1] + ua * (p2[1] - p1[1])
        return [x, y]

    return None

def split_segment(segment, point):
    p1, p2 = segment
    return [ [p1, point], [point, p2] ]

def point_on_segment(p, segment, eps=1e-6):
    """Check if point p is on segment [a, b]"""
    a, b = segment
    x, y = p
    x1, y1 = a
    x2, y2 = b

    cross = (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)
    if abs(cross) > eps:
        return False

    dot = (x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)
    if dot < 0:
        return False

    squared_len = (x2 - x1)**2 + (y2 - y1)**2
    if dot > squared_len:
        return False

    return True