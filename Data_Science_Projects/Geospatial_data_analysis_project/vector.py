
import json
import os
import webbrowser
import math
from collections import defaultdict

import folium # Show maps
import pyproj # Convert coordinates

import utilities




class Vector():

    def __init__(self, geometry='point'):

        # Attributes

        if geometry.upper() not in ['POINT', 'POLYLINE', 'POLYGON']:
            self._geometry = None
        else:
            self._geometry = geometry.upper()

        self._source = None
        self._format = None
        self._epsg = None # Reference system

        self._coordinates = []
        self._attributes = []

        self._bbox = None # Bounding box

        self._selection = None

        self._cleaned = False


    def __repr__(self):

        report = {
            'geometry': self._geometry,
            'source': self._source,
            'format': self._format,
            'epsg': self._epsg,
            'coordinates': len(self._coordinates),
            'attributes': len(self._attributes),
            'bbox': self._bbox
        }

        return json.dumps(report, indent=4)
        

    # Properties

    def _get_epsg(self):
        return self._epsg

    def _set_epsg(self, epsg_code):

        # TODO: Check epsg_code is a valid code

        self._epsg = epsg_code

    epsg = property(fget=_get_epsg, fset=_set_epsg)


    def _get_coordinates(self):
        return self._coordinates

    coordinates = property(fget=_get_coordinates)


    def _get_attributes(self):
        return self._attributes
    
    attributes = property(fget=_get_attributes)


    def _get_fields(self):

        if (self._attributes) == 0:
            return []

        return list(self._attributes[0].keys())

    fields = property(fget=_get_fields)


    def _get_selection(self):
        return self._selection
    
    selection = property(fget=_get_selection)

    def _get_cleaned(self):
        return self._cleaned

    is_cleaned = property(fget=_get_cleaned)
    
    
    # User methods

    def random_points(self, n, x_min, y_min, x_max, y_max):

        # TODO: Check instance of type 'POINT'
        
        coordinates, attributes = utilities.random_points(
            n, x_min, y_min, x_max, y_max
        )

        self._source = 'random'
        self._format = 'list'

        self._geometry = 'POINT'

        self._coordinates = coordinates
        self._attributes = attributes

    
    def bounding_box(self):

        if len(self._coordinates) == 0:
            utilities.warning('No coordinates found.')
            return

        if self._geometry == 'POINT':
            x_min, y_min = self._coordinates[0]
            x_max, y_max = self._coordinates[0]

            for point in self._coordinates:
                x, y = point

                if x < x_min:
                    x_min = x
                elif x > x_max:
                    x_max = x

                if y < y_min:
                    y_min = y
                elif y > y_max:
                    y_max = y

            
            self._bbox = [x_min, y_min, x_max, y_max]
        elif self._geometry == 'POLYLINE':
            pass
        elif self._geometry == 'POLYGON':
            pass

        
    def osm(self):

        if len(self._coordinates) == 0:
            utilities.warning('No coordinates found.')
            return

        if self._epsg is None:
            utilities.warning('No EPSG code found.')
            return        

        if self._epsg != 4326:
            # TODO: project coordinates
            pass

        # Create layer
        osm_layer = utilities.create_osm_layer(self)

        # Draw layer
        utilities.draw_osm_map([osm_layer])


    def add_field(self, name, default=None, overwrite=False):

        if len(self._attributes) == 0:
            utilities.warning('No attributes found in current dataset.')
            return

        if name in self.fields and overwrite is False:
            utilities.warning(f'Field {name} already exists in current dataset.')
            return

        for record in self._attributes:
            record[name] = default


    def add_geometric_fields(self):
        
        if len(self._attributes) == 0:
            utilities.warning('No attributes found in current dataset.')
            return

        if self._geometry == 'POINT':

            for count, point in enumerate(self.coordinates):
                x, y = point

                self._attributes[count]['x'] = x
                self._attributes[count]['y'] = y

        elif self._geometry == 'POLYLINE':

            for count, polyline in enumerate(self.coordinates):
                self._attributes[count]['length'] = utilities.length(polyline)
                
        elif self._geometry == 'POLYGON':

            for count, polygon in enumerate(self.coordinates):

                x, y = utilities.centroid(polygon) 

                self._attributes[count]['x_centroid'] = x
                self._attributes[count]['y_centroid'] = y

                self._attributes[count]['perimeter'] = utilities.perimeter(polygon)
                self._attributes[count]['area'] = utilities.area(polygon)


    def select(self, expression):
        """Create selection set based on expression. Ignore previous selection"""
        
        if len(self._attributes) == 0:
            utilities.warning('No attributes found in current dataset.')
            return

        # Validate expression with ast

        validation = utilities.validate(expression)

        print(json.dumps(validation, indent=4))

        if validation['status'] is False:
            utilities.warning(validation['message'])
            return

        # Create selection set

        selection = []

        for record_count, record in enumerate(self._attributes):

            values = []

            for label in validation['tokens']['label']:
                values.append(record[label])

            # Set variables
            for label_count, label in enumerate(validation['tokens']['label']):
                exec(f'{label} = {values[label_count]}')

            # Evaluate expression
            if eval(expression) is True: # This can be dangerous!!!!!!!!!
                selection.append(record_count)

        # Update selection set
        self._selection = selection


    def clear(self):
        self._selection = None


    def calculate(self, target, expression):
        """
        Assign a value to a target field, for instance:

            dataset.calculate('colour', '"green"')
            dataset.calculate('size', '10')
            dataset.calculate('size', 'x + 10')            
        """
        
        if len(self._attributes) == 0:
            utilities.warning('No attributes found in current dataset.')
            return
        
        validation = utilities.validate(expression)

        if validation['status'] is False:
            utilities.warning(validation['message'])
            return

        # Check labels (fields) exist in dataset

        for label in validation['tokens']['label']:
            if label not in self.fields:
                utilities.error(f'Field "{label}" not found.')
                return

        # Records to update
        if self._selection is None:
            records = range(len(self._attributes))
        else:
            records = self._selection

        # Ensure target field exists
        if target not in self.fields:
            self.add_field(target)

        # Calculate field
        for record_count in records:
            values = []

            for label in validation['tokens']['label']:
                values.append(self._attributes[record_count][label])

            # Set variables
            for label_count, label in enumerate(validation['tokens']['label']):
                exec(f'{label} = {values[label_count]}')

            # Evaluate calculation
            self._attributes[record_count][target] = eval(expression)
            # This can be dangerous!!!!!!!!!

        
    def read_csv(self, id_field, x_field, y_field, filename=None, separator=','):

        if filename is None:
            filename = utilities.input_file(['csv'])

        if filename is None:
            return

        if self._geometry == 'POINT':
            coordinates, attributes = utilities.read_points_csv(
                filename, id_field, x_field, y_field, separator
            )
        elif self._geometry == 'POLYLINE':
            coordinates, attributes = utilities.read_polylines_csv(
                filename, id_field, x_field, y_field, separator
            )
        elif self._geometry == 'POLYGON':
            coordinates, attributes = utilities.read_polygons_csv(
                filename, id_field, x_field, y_field, separator
            )

        # Update Vector() instance
        self._coordinates = coordinates
        self._attributes = attributes

        self._source = filename
        self._format = 'CSV'


    def read_geojson(self, filename=None):

            if filename is None:
                filename = utilities.input_file(['geojson'])

            if filename is None:
                return

            if self._geometry == 'POINT':
                dataset = utilities.read_geojson(filename, 'Point')
            if self._geometry == 'POLYLINE':
                dataset = utilities.read_geojson(filename, 'LineString')
            if self._geometry == 'POLYGON':
                dataset = utilities.read_geojson(filename, 'Polygon')

            if dataset is None:
                utilities.error(f'Error reading file:\n{filename}')
                return

            # Update Vector() instance
            coordinates, attributes, epsg = dataset
            
            self._coordinates = coordinates
            self._attributes = attributes
            self._epsg = epsg

            self._source = filename
            self._format = 'GeoJSON'
        
    def write_csv(self, filename=None, epsg=None, world_file=None):

        if filename is None:
            filename = utilities.output_file(['csv'])

        if filename is None:
            return

        if not filename.endswith('.csv'):
            filename += '.csv'
            
        if self._geometry == 'POINT':
            utilities.write_points_csv(self, filename, epsg, world_file)
        elif self._geometry == 'POLYLINE':
            pass
        elif self._geometry == 'POLYGON':
            pass

    def clean(self):
        """Detect intersections and remove dangling segments for POLYLINE datasets."""
        if self._geometry != 'POLYLINE':
            utilities.warning("Clean only works for POLYLINE datasets.")
            return

        # Flatten all polylines into raw segments
        raw_segments = []
        for polyline in self._coordinates:
            for i in range(len(polyline) - 1):
                raw_segments.append((polyline[i], polyline[i + 1]))

        # Step 1: Collect intersection points
        intersection_points = set()
        for i in range(len(raw_segments)):
            for j in range(i + 1, len(raw_segments)):
                inter = utilities.segment_intersection(raw_segments[i], raw_segments[j])
                if inter:
                    intersection_points.add(tuple(inter))

        # Step 2: Split each segment by intersection points
        split_segments = []
        for seg in raw_segments:
            points = [tuple(seg[0]), tuple(seg[1])]
            for ip in intersection_points:
                if utilities.point_on_segment(ip, seg):
                    points.append(ip)
            # Sort points along the segment direction
            points = sorted(points, key=lambda p: ((p[0] - points[0][0]) ** 2 + (p[1] - points[0][1]) ** 2))
            for i in range(len(points) - 1):
                a, b = points[i], points[i + 1]
                if a != b:
                    split_segments.append((a, b))

        # Step 3: Remove duplicates and build adjacency
        edges_set = set()
        adjacency = defaultdict(list)

        for a, b in split_segments:
            a, b = tuple(a), tuple(b)
            if a != b:
                edge = (a, b) if a < b else (b, a)
                edges_set.add(edge)
                adjacency[a].append(b)
                adjacency[b].append(a)

        # Step 4: Remove dangling nodes (degree = 1)
        changed = True
        while changed:
            changed = False
            for node in list(adjacency.keys()):
                if len(adjacency[node]) == 1:
                    neighbor = adjacency[node][0]
                    adjacency[neighbor].remove(node)
                    del adjacency[node]
                    changed = True

        # Step 5: Update cleaned vector
        cleaned = []
        for a in adjacency:
            for b in adjacency[a]:
                if tuple(a) < tuple(b):
                    cleaned.append([list(a), list(b)])

        self._coordinates = cleaned
        self._attributes = [{} for _ in self._coordinates]
        self._cleaned = True

    def topology(self):
        """Construct polygons from a cleaned polyline graph."""
        if self._geometry != 'POLYLINE' or not hasattr(self, '_cleaned') or not self._cleaned:
            return

        import math
        from collections import defaultdict

        edge_dict = defaultdict(list)
        directed_edges = []

        for seg in self._coordinates:
            a = tuple(seg[0])
            b = tuple(seg[1])

            # Add forward edge
            angle_ab = math.atan2(b[1] - a[1], b[0] - a[0])
            directed_edges.append((a, b, angle_ab))
            edge_dict[a].append((b, angle_ab))

            # Add reverse edge
            angle_ba = math.atan2(a[1] - b[1], a[0] - b[0])
            directed_edges.append((b, a, angle_ba))
            edge_dict[b].append((a, angle_ba))

        for a, b, t in directed_edges:
            print(f"  {a} -> {b} (angle: {t:.2f})")

        # Sort adjacency lists
        for node in edge_dict:
            edge_dict[node].sort(key=lambda x: x[1])

        visited = set()
        polygons = []

        def walk_ring(start_edge):
            ring = []
            a, b = start_edge
            ring.append(a)
            current = a
            next_node = b

            while True:
                ring.append(next_node)
                visited.add((current, next_node))
                neighbors = edge_dict[next_node]
                found = False
                for i, (n, _) in enumerate(neighbors):
                    if n == current:
                        next_i = (i + 1) % len(neighbors)
                        new_edge = (next_node, neighbors[next_i][0])
                        if new_edge in visited:
                            return None
                        current, next_node = new_edge
                        found = True
                        break
                if not found:
                    return None
                if next_node == ring[0]:
                    break
            return ring

        for a, b, _ in directed_edges:
            if (a, b) in visited:
                continue
            ring = walk_ring((a, b))
            if ring and len(ring) > 3:
                if ring[0] != ring[-1]:
                    ring.append(ring[0])
                polygons.append([ring])



        if len(polygons) > 1:
            polygons.sort(key=lambda poly: self.polygon_area(poly[0]))
            polygons = polygons[:-1]  # remove largest
        poly_vec = Vector(geometry='polygon')
        poly_vec._coordinates = polygons
        poly_vec._attributes = [{'id': i} for i in range(len(polygons))]
        poly_vec._epsg = self._epsg

        return poly_vec

    # Remove outer polygon (the largest by area)
    def polygon_area(self, ring):
        area = 0
        for i in range(len(ring) - 1):
            x1, y1 = ring[i]
            x2, y2 = ring[i + 1]
            area += (x1 * y2 - x2 * y1)
        return abs(area) / 2


        
