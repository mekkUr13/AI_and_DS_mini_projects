
import geo_2025 as geo



# 1. Callback functions ~ called from events such as mouse click, ....

def draw_one_point(event):

    x = 400
    y = 300

    point = [x, y]
    
    screen.draw_point([x, y], colour='green', size=10)


def draw_one_polyline(event):

    point_1 = [300, 0]
    point_2 = [300, 600]

    polyline = [point_1, point_2]

    screen.draw_polyline(polyline)


def print_digit_points(event):

    print(screen._digit)



    
# 2. Screen() instance
screen = geo.Screen()

# 3. Bindings

screen.keyboard_bind('1', draw_one_point)
screen.keyboard_bind('2', draw_one_polyline)

screen.keyboard_bind('3', print_digit_points)



# 4. Main loop
screen.loop()
