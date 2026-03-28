import geo_2025 as geo
import os

# 1. Create polyline dataset
dataset = geo.Vector(geometry='polyline')
dataset._coordinates = [
    [[0, 0], [0, 100]],
    [[0, 100], [100, 100]],
    [[100, 100], [100, 0]],
    [[100, 0], [0, 0]],
    [[0, 100], [100, 0]],
    [[100, 100], [0, 0]]
]
dataset.epsg = 4326

# 2. Clean the dataset
dataset.clean()

# 3. Call topology() on the SAME object
polygon_vector = dataset.topology()

# 4. Output result
if polygon_vector:
    print(f"Found {len(polygon_vector.coordinates)} polygons")
    for poly in polygon_vector.coordinates:
        print(poly)
    polygon_vector.osm()
else:
    print("No polygons generated.")