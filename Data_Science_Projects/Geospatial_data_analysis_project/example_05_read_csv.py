
import geo_2025 as geo


dataset = geo.Vector()

print()
print(dataset)

# Read data from CSV
dataset.read_csv('ID', 'X', 'Y')

dataset.epsg = 4326

print()
print(dataset)

dataset.osm()
