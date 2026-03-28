
import geo_2025 as geo

dataset = geo.Vector(geometry='polygon')

dataset.read_geojson()

print(dataset.coordinates)

dataset.osm()
