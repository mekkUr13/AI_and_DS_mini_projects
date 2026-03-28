
import json
import tkinter

import utilities


class Raster():

    def __init__(self):

        self._filename = None
        self._epsg = None
        self._photoimage = None # Tkinter image format
        self._world_file = None

    def __repr__(self):

        report = {
            'filename': self._filename,
            'epsg': self._epsg,
            'world': self._world_file
        }

        return json.dumps(report, indent=4)


    # Properties

    def _get_epsg(self):
        return self._epsg

    def _set_epsg(self, epsg_code):

        # TODO: Check epsg_code is a valid code

        self._epsg = epsg_code

    epsg = property(fget=_get_epsg, fset=_set_epsg)


    def _get_shape(self):

        if self._photoimage is None:
            return

        rows = self._photoimage.height()
        columns = self._photoimage.width()

        return [rows, columns]

    shape = property(fget=_get_shape)


    # User methods

    def read_image(self):

        # Get filename

        filename = utilities.input_file(['png'])

        if filename is None:
            return

        # Update Raster() instance
        self._photoimage = tkinter.PhotoImage(file=filename)
        self._filename = filename

        # World file
        world_file = utilities.read_world_file(filename)
        self._world_file = world_file

        
    
