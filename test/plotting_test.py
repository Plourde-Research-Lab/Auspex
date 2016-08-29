# Copyright 2016 Raytheon BBN Technologies
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0

import asyncio
import os
import numpy as np
import sys

from pycontrol.instruments.instrument import SCPIInstrument, StringCommand, FloatCommand, IntCommand
from pycontrol.experiment import Experiment, FloatParameter
from pycontrol.stream import DataStream, DataAxis, DataStreamDescriptor, OutputConnector
from pycontrol.filters.plot import Plotter
from pycontrol.filters.average import Average
from pycontrol.filters.debug import Print
from pycontrol.filters.channelizer import Channelizer
from pycontrol.filters.integrator import KernelIntegrator

from pycontrol.log import logger, logging
logger.setLevel(logging.INFO)

class TestInstrument(SCPIInstrument):
    frequency = FloatCommand(get_string="frequency?", set_string="frequency {:g}", value_range=(0.1, 10))
    serial_number = IntCommand(get_string="serial?")
    mode = StringCommand(name="enumerated mode", scpi_string=":mode", allowed_values=["A", "B", "C"])

class TestExperiment(Experiment):
    """Here the run loop merely spews data until it fills up the stream. """

    # Create instances of instruments
    fake_instr_1 = TestInstrument("FAKE::RESOURE::NAME")

    # Parameters
    field = FloatParameter(unit="Oe")
    freq  = FloatParameter(unit="Hz")

    # DataStreams
    voltage = OutputConnector()

    # Constants
    num_samples     = 1024
    delays          = 1e-9*np.arange(100, 10001,100)
    round_robins    = 2
    sampling_period = 2e-9
    T2              = 5e-6

    def init_instruments(self):
        pass

    def init_streams(self):
        # Add a "base" data axis: say we are averaging 5 samples per trigger
        descrip = DataStreamDescriptor()
        descrip.add_axis(DataAxis("samples", 2e-9*np.arange(self.num_samples)))
        descrip.add_axis(DataAxis("delay", self.delays))
        descrip.add_axis(DataAxis("round robins", np.arange(self.round_robins)))
        self.voltage.set_descriptor(descrip)

    def __repr__(self):
        return "<SweptTestExperiment>"

    async def run(self):
        pulse_start = 250
        pulse_width = 700

        #fake the response for a Ramsey frequency experiment with a gaussian excitation profile
        idx = 0
        for _ in range(self.round_robins):
            for delay in self.delays:
                if idx == 0:
                    records = np.zeros((5, self.num_samples))
                await asyncio.sleep(0.01)
                records[idx,pulse_start:pulse_start+pulse_width] = np.exp(-0.5*(self.freq.value/2e6)**2) * \
                                                              np.exp(-delay/self.T2) * \
                                                              np.sin(2*np.pi * 10e6 * self.sampling_period*np.arange(pulse_width) \
                                                              + np.cos(2*np.pi * self.freq.value * delay))

                #add noise
                records[idx] += 0.1*np.random.randn(self.num_samples)

                if idx == 4:
                    await self.voltage.push(records.flatten())
                    idx = 0
                else:
                    idx += 1

        logger.debug("Stream has filled {} of {} points".format(self.voltage.points_taken, self.voltage.num_points() ))

if __name__ == '__main__':

    exp = TestExperiment()
    channelizer = Channelizer(10e6, 0.05, 8, name="Demod")
    ki = KernelIntegrator(np.ones(32), name="KI")
    avg1 = Average("round robins", name="Average channelizer RRs")
    avg2 = Average("round robins", name="Average KI RRs")
    pl1 = Plotter(name="2D Scope", plot_dims=2, palette="Spectral11")
    pl2 = Plotter(name="Demod", plot_dims=2, palette="Spectral11")
    pl3 = Plotter(name="KI", plot_dims=1)
    # pl4 = Plotter(name="KI", plot_dims=2, palette="Spectral11")

    edges = [
            (exp.voltage, channelizer.sink),
            (channelizer.source, avg1.data),
            (channelizer.source, ki.sink),
            (ki.source, avg2.data),
            (avg1.final_average, pl2.data),
            (avg2.final_average, pl3.data)
            ]

    exp.set_graph(edges)

    exp.init_instruments()
    exp.add_sweep(exp.freq, 1e6*np.linspace(-0.1,0.1,3))
    exp.init_progressbar(num=1)
    exp.run_sweeps()
