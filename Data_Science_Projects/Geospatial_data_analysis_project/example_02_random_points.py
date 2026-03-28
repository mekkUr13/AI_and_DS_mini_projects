
import geo_2025 as geo



# Vector dataset

dataset = geo.Vector()

print(dataset)





dataset.random_points(300, -180, -90, 180, 90)

print(dataset)

print()
print(dataset.epsg)

dataset.epsg = 4326

print()
print(dataset.epsg)

print()
print(dataset)

print(dataset.coordinates)

print(dataset.attributes)

dataset.bounding_box()

print()
print(dataset)


