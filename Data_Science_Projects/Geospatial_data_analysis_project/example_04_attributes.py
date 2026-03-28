
import geo_2025 as geo



# Vector dataset
dataset = geo.Vector()
print(dataset)
dataset.random_points(300, -180, -90, 180, 90)
print(dataset)
dataset.epsg = 4326


# Test add_field()

print(dataset.fields)
dataset.add_field('colour', 'green')
print(dataset.fields)
dataset.add_field('colour', 'blue', overwrite=True)


# Test add_geometric_fields()
dataset.add_geometric_fields()
print(dataset.fields)


# Test select()

##dataset.select('x ~ 0.0')
dataset.select('x < 0.0 and y > 0.0')
##dataset.select("os.system('rm -rf /')")

print(dataset.selection)

# Test clear()
dataset.clear()
print(dataset.selection)

# Test select() + calculate()

dataset.select('x < 0.0 and y > 0.0')
dataset.calculate('colour', '"purple"')

dataset.select('x < 0.0 and y < 0.0')
dataset.calculate('colour', '"red"')

dataset.select('x > 0.0 and y > 0.0')
dataset.calculate('colour', '"blue"')

dataset.select('x > 0.0 and y < 0.0')
dataset.calculate('colour', '"orange"')


dataset.osm()





for record in dataset.attributes[:10]:
    print(record)



