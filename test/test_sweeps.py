import unittest
import asyncio
import numpy as np

from pycontrol.instruments.instrument import Instrument, StringCommand, FloatCommand, IntCommand
from pycontrol.experiment import Experiment, FloatParameter, Quantity
from pycontrol.stream import DataStream, DataAxis, DataStreamDescriptor

class TestInstrument1(Instrument):
    frequency = FloatCommand(get_string="frequency?", set_string="frequency {:g}", value_range=(0.1, 10))
    serial_number = IntCommand(get_string="serial?")
    mode = StringCommand(scpi_string=":mode", allowed_values=["A", "B", "C"])

class TestExperiment(Experiment):

    # Create instances of instruments
    fake_instr_1 = TestInstrument1("FAKE::RESOURE::NAME")

    # Parameters
    field = FloatParameter(unit="Oe")
    freq  = FloatParameter(unit="Hz")

    # DataStreams
    voltage = DataStream(unit="V")

    # Constants
    samples    = 5

    def init_streams(self):
        # Add a "base" data axis: say we are averaging 5 samples per trigger
        descrip = DataStreamDescriptor()
        descrip.add_axis(DataAxis("samples", range(self.samples)))
        self.voltage.set_descriptor(descrip)

    async def run(self):
        for s in self._output_streams.values():
            s.reset()

        print("Data taker running")
        time_val = 0
        time_step = 0.1
        
        while True:
            #Produce fake noisy sinusoid data every 0.02 seconds until we have 1000 points
            if self._output_streams['voltage'].done():
                print("Data taker finished.")
                break
            await asyncio.sleep(0.01)
            
            print("Stream has filled {} of {} points".format(self._output_streams['voltage'].points_taken, self._output_streams['voltage'].num_points() ))
            data_row = np.sin(2*np.pi*1e3*time_val) + 0.1*np.random.random(self.samples)       
            time_val += time_step
            await self.voltage.push(data_row)

class SweepTestCase(unittest.TestCase):
    """
    Tests sweeping
    """

    def test_add_sweep(self):
        exp = TestExperiment()
        exp.add_sweep(exp.field, np.linspace(0,100.0,11))

if __name__ == '__main__':
    unittest.main()