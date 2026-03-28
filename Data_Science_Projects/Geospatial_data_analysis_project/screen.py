
import json
import tkinter
import tkinter.simpledialog

import pyproj

from vector import Vector
from raster import Raster

import utilities


class Screen():

    def __init__(self, rows=600, columns=800, background='black'):

        self._rows = rows
        self._columns = columns

        # Root window

        self._root = tkinter.Tk()

        self._root.title('GEO 2025')
        self._root.resizable(False, False)

        # Canvas

        self._canvas = tkinter.Canvas(
            self._root, width=self._columns, height=self._rows,
            bg=background, borderwidth=0, highlightthickness=0
        )

        self._canvas.pack()

        self._epsg = None # Local coordinates
        self._world_file = [1, 0, 0, -1, 0, self._rows]


        # System bindings

        # F1-F4

        self._root.bind('<F1>', self._help)

        # F5-F8

        self._root.bind('<F5>', self._read_and_draw_image)
        

        # F9-F12

        self._root.bind('<F9>', self._start_digit)
        self._root.bind('<F10>', self._stop_digit)
        self._root.bind('<F11>', self._digit_to_csv)

        # Datasets

        self._digit = Vector(geometry='point') # Layer of digitised points

        self._points = Vector(geometry='point')
        self._polylines = Vector(geometry='polyline')
        self._polygons = Vector(geometry='polygon')

        self._image = Raster()

        
        


    # Reserved methods

    def _start_digit(self, event):
        self._root.bind('<Button-1>', self._get_point) # Left button click
        self.cursor('tcross')

    def _stop_digit(self, event):
        self._root.unbind('<Button-1>')
        self.cursor()

        self._canvas.event_generate('<Button-1>')

    def _get_point(self, event):

        #print(event.x, event.y)

        point = [event.x, event.y]
        count = len(self._digit.coordinates)

        self._digit._coordinates.append(point)
        self._digit._attributes.append({'id': count})

        self.draw_point(point)

        if self._digit._source is None:
            self._digit._source = 'digit'


    def _help(self, event):

        help_text = 'F1: Help\n'

        help_text += '\n'
        help_text += 'F5: Read and draw an image\n'
        help_text += '\n'
        help_text += 'F9: Start digitising\n'
        help_text += 'F10: Stop digitising\n'
        help_text += 'F11: Save digitised points to CSV format\n'

        print(help_text)


    def _digit_to_csv(self, event):

        if len(self._digit.coordinates) == 0:
            utilities.warning('Digitised ponts not found.')
            return

        if self._image._photoimage is not None:
            epsg = self._image._epsg
            world_file = self._image._world_file
        else:
            epsg = self._epsg
            world_file = self._world_file
        
        self._digit.write_csv(epsg=epsg, world_file=world_file)


    def _read_and_draw_image(self, event):

        self._image.read_image()
        self.draw_image()

        

    # User methods

    def loop(self):
        self._root.mainloop()

    def keyboard_bind(self, event, function):
        self._root.bind(event, function)

    def keyboard_unbind(self, event):
        self._root.unbind(event)
        
    def mouse_bind(self, event, function):
        self._canvas.bind(event, function)

    def mouse_unbind(self, event):
        self._canvas.unbind(event)

    def cursor(self, shape=''):
        self._canvas.config(cursor=shape)


    # Graphical methods

    def draw_point(self, point, size=3, colour='white', tag='point'):

        x, y = point

        x_min = x - size
        x_max = x + size
        y_min = y - size
        y_max = y + size

        self._canvas.create_rectangle(
            x_min, y_min, x_max, y_max, fill=colour, tag=tag
        )


    def draw_polyline(self, polyline, width=2, colour='white', tag='polyline'):

        self._canvas.create_line(
            polyline, fill=colour, width=width, tag=tag
        )


    def draw_image(self):

        global image

        image = self._image._photoimage

        if image is None:
            # Warning
            return

        self._canvas.create_image(0, 0, image=image, anchor='nw')
        
        # Insert point (0,0) in canvas coordinates
        # 'nw' upper-left corner of the image

        
        











        
