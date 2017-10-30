from auspex.experiment import FloatParameter, IntParameter, Experiment
from auspex.stream import DataStream, DataAxis, DataStreamDescriptor, OutputConnector
from auspex.filters import Print, WriteToHDF5, Plotter, XYPlotter, Averager
from auspex.instruments import SynthHD
from auspex.log import logger

import asyncio
import numpy as np
import time

class DumbExperiment(Experiment):
    freq = FloatParameter(default = 5e9, unit="Hz")

    output = OutputConnector()

    wf = SynthHD('COM3')

    freqs = np.linspace(4e9, 6e9, 11)

    def init_instruments(self):
        self.freq.assign_method(self.wf.set_ch1frequency)

    def init_streams(self):
        ax = DataAxis("Frequency", [1])
        self.output.add_axis(ax)

    async def run(self):
        self.wf.set_ch1frequency(self.freq)
        await self.output.push(self.wf.ch1frequency)
