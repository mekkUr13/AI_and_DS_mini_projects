
import geo_2025 as geo


##
### test Raster () class
##
##image = geo.Raster()
##
##print(image)
##
##image.read_image()
##
##print(image)
##
##print(image.shape)





# 1. Screen() instance
screen = geo.Screen()

# 2. Callback functions

def set_screen_to_geographic_world_file(event):

    world_file = [
        360 / screen._columns,
        0,
        0,
        -180 / screen._rows,
        -180,
        90
    ]

    geographic = geo.Vector()

    for count, point in enumerate(screen._digit.coordinates):
        geo_point = geo.utilities.screen_to_world(point, world_file)

        geographic._coordinates.append(geo_point)

        geographic._attributes.append(screen._digit.attributes[count])
        
    geographic.epsg = 4326
    geographic.osm()
        

# 3. Bindings

screen.keyboard_bind('1', set_screen_to_geographic_world_file)


# 4. Loop
screen.loop()

