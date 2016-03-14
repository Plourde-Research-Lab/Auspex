import logging
import threading
import subprocess
import time
import os

import numpy as np

# Bokeh
import h5py

from bokeh.plotting import figure

from bokeh.models.renderers import GlyphRenderer

class BokehServerThread(threading.Thread):
    def __init__(self):
        super(BokehServerThread, self).__init__()
        self.daemon = True

    def __del__(self):
        self.join()

    def run(self):
        self.p = subprocess.Popen(["bokeh", "serve"], env=os.environ.copy())

    def join(self, timeout=None):
        print("Trying to kill server thread {}".format(self.p.pid))
        self.p.kill()
        super(BokehServerThread, self).join(timeout=timeout)

class MultiPlotter(object):
    """Attach a plotter to the sweep."""
    def __init__(self, title, xs, ys, **plot_args):
        super(MultiPlotter, self).__init__()
        self.title = title
        self.filename = title.replace(' ', '_')
        self.update_interval = 0.5
        self.last_update = time.time()

        assert len(xs) == len(ys)

        # These are parameters and quantities
        self.xs = xs
        self.ys = ys

        # Data containers
        self.x_data = [[] for x in self.xs]
        self.y_data = [[] for y in self.ys]

        # Figure
        self.figure = figure(plot_width=400, plot_height=400)
        self.plot = self.figure.multi_line(self.x_data, self.y_data, name=self.title, **plot_args)
        renderers = self.plot.select(dict(name=title))
        self.renderer = [r for r in renderers if isinstance(r, GlyphRenderer)][0]
        self.data_source = self.renderer.data_source

    def update(self, force=False):
        for x, y, xd, yd in zip(self.xs, self.ys, self.x_data, self.y_data):
            xd.append(x.value)
            yd.append(y.value)
        if (time.time() - self.last_update >= self.update_interval) or force:
            # for i, (x,y) in enumerate(zip(self.x_data, self.y_data)):
            self.data_source.data["xs"] = np.copy(self.x_data)
            self.data_source.data["ys"] = np.copy(self.y_data)
            self.last_update = time.time()

    def clear(self):
        self.x_data = [[] for x in self.xs]
        self.y_data = [[] for y in self.ys]

class Plotter(object):
    """Attach a plotter to the sweep."""
    def __init__(self, title, x, y, **plot_args):
        super(Plotter, self).__init__()
        self.title = title
        self.filename = title.replace(' ', '_')
        self.update_interval = 0.5
        self.last_update = time.time()

        # Pop the figure arguments
        self.fig_args = {'x_axis_type': plot_args.pop('x_axis_type'),
                         'y_axis_type': plot_args.pop('y_axis_type')}

        # These are parameters and quantities
        self.x = x
        self.y = y

        # Data containers
        self.x_data = []
        self.y_data = []

        # Figure
        self.xlabel = self.x.name + (" ("+self.x.unit+")" if self.x.unit is not None else '')
        self.ylabel = self.y.name + (" ("+self.y.unit+")" if self.y.unit is not None else '')
        self.figure = figure(plot_width=400, plot_height=400, title=self.title,
                             x_axis_label=self.xlabel, y_axis_label=self.ylabel, **self.fig_args)
        self.plot = self.figure.line([],[], name=title, **plot_args)
        renderers = self.plot.select(dict(name=title))
        self.renderer = [r for r in renderers if isinstance(r, GlyphRenderer)][0]
        self.data_source = self.renderer.data_source

    def update(self, force=False):
        self.x_data.append(self.x.value)
        self.y_data.append(self.y.value)
        if (time.time() - self.last_update >= self.update_interval) or force:
            self.data_source.data["x"] = np.copy(self.x_data)
            self.data_source.data["y"] = np.copy(self.y_data)
            self.last_update = time.time()

    def clear(self):
        self.x_data = []
        self.y_data = []

class Plotter2D(object):
    """Attach a plotter to the sweep."""
    def __init__(self, title, x, y, z, **plot_args):
        super(Plotter2D, self).__init__()
        self.title = title
        self.filename = title.replace(' ', '_')
        self.update_interval = 0.5
        self.last_update = time.time()

        # Figure
        xmax = max(x.values)
        ymax = max(y.values)
        xmin = min(x.values)
        ymin = min(y.values)

        # Mesh grid of x and y values from the sweep
        self.x_mesh, self.y_mesh = np.meshgrid(x.values, y.values)
        self.z_data = np.zeros_like(self.x_mesh)

        # These are parameters and quantities
        self.x = x
        self.y = y
        self.z = z

        # Construct the plot
        self.xlabel = self.x.name + (" ("+self.x.unit+")" if self.x.unit is not None else '')
        self.ylabel = self.y.name + (" ("+self.y.unit+")" if self.y.unit is not None else '')
        self.figure = figure(x_range=[xmin, xmax], y_range=[ymin, ymax], plot_width=400, plot_height=400,
                             x_axis_label=self.xlabel, y_axis_label=self.ylabel, title=self.title)
        self.plot = self.figure.image(image=[self.z_data], x=[xmin], y=[ymin],
                                      dw=[xmax-xmin], dh=[ymax-ymin], name=self.title, **plot_args)
        renderers = self.plot.select(dict(name=title))
        self.renderer = [r for r in renderers if isinstance(r, GlyphRenderer)][0]
        self.data_source = self.renderer.data_source

    def update(self, force=False):
        # Find the coordinates and then set the array element
        new_data_loc = np.where(  np.logical_and(self.x_mesh == self.x.value, self.y_mesh == self.y.value)  )
        self.z_data[new_data_loc] = self.z.value
        if (time.time() - self.last_update >= self.update_interval) or force:
            self.data_source.data["image"] = [self.z_data]
            self.last_update = time.time()

    def clear(self):
        self.x_data = []
        self.y_data = []
        self.z_data = []
