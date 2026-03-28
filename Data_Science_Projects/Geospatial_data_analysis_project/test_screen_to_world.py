# Test utilities.screen_to_world

import geo_2025 as geo

x = 128
y = 600 - 381

world_file = [0.45, 0, 0, -0.3, -180, 90]

w = geo.utilities.screen_to_world([x, y], world_file)


print(w)
