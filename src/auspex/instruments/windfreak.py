# Copyright 2016 Raytheon BBN Technologies
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0

__all__ = ['SynthHD']

from .instrument import SCPIInstrument, Command, StringCommand, FloatCommand, IntCommand
from auspex.log import logger
import time
import numpy as np
import socket

class SynthHD(SCPIInstrument):
    """SCPI instrument driver for WindFreak SynthHD Signal Generator.

    Properties:
        frequency: Set the RF generator frequency, in MHz. 0.054-13.6 GHz.
        power: Set the RF generator output power, in dBm. -60 - +20 dBm.
        output: Toggle RF signal output on/off.
        pulse: Toggle RF pulsed mode on/off.
        alc: Toggle source Auto Leveling on/off.
        mod: Toggle amplitude modulation on/off.
        pulse_source: Set pulse trigger to INTERNAL or EXTERNAL.
        freq_source: Set frequency source to INTERNAL or EXTERNAL.
    """
    instrument_type = "Microwave Source"
    ch1frequency = FloatCommand(get_string="C0f?", set_string="C0f{:f}")
    ch1power     = FloatCommand(get_string="C0W?", set_string="C0W{:f}")
    ch2frequency = FloatCommand(get_string="C1f?", set_string="C1f{:f}")
    ch2power     = FloatCommand(get_string="C1W?", set_string="C1W{:f}")

    # output    = Command(get_string="r?", set_string="r",
    #                     value_map={True: '0', False: '1'})
    # freq_source  = StringCommand(scpi_string="x",
    #                       value_map={'INTERNAL 10MHz': '2',
    #                                  'INTERNAL 27MHz': '1',
    #                                  'EXTERNAL': '0'})

    def __init__(self, resource_name=None, *args, **kwargs):
        super(SynthHD, self).__init__(resource_name, *args, **kwargs)

    def connect(self, resource_name=None, interface_type="VISA"):
        if resource_name is not None:
            self.resource_name = resource_name

        # print(self.resource_name)
        super(SynthHD, self).connect(resource_name=resource_name, interface_type=interface_type)
        self.interface._resource.read_termination = u""
        self.interface._resource.write_termination = u""
        self.interface._resource.timeout = 3000 #seem to have trouble timing out on first query sometimes

    # def get_frequency(self, channel):
    #     return float(self.interface.query("C{:d}f?".format(channel)))*1e6
    #
    # def set_frequency(self, channel, value):
    #     self.interface.write("C{:d}f{:f}".format(channel, value/1e6))
    #
    # def get_power(self, channel):
    #     return float(self.interface.query("C{:d}W?".format(channel)))
    #
    # def set_power(self, channel, value):
    #     self.interface.write("C{:d}W{:f}".format(channel, value))
    #
    # def get_output(self, channel):
    #     return int(self.interface.query("C{:d}r?".format(channel)))
    #
    # def set_output(self, channel, value):
    #     self.interface.write("C{:d}r{:d}".format(channel, value))
    #
    #     # Channel Specific
    # def get_ch1frequency(self):
    #     return float(self.interface.query("C0f?"))*1e6
    #
    # def set_ch1frequency(self, value):
    #     self.interface.write("C0f{:f}".format(value/1e6))
    #
    # def get_ch1power(self):
    #     return float(self.interface.query("C0W?"))
    #
    # def set_ch1power(self, value):
    #     self.interface.write("C0W{:f}".format(value))
    #
    # def get_ch1output(self):
    #     return int(self.interface.query("C0r?".format))
    #
    # def set_ch1output(self, value):
    #     self.interface.write("C0r{:d}".format(value))
    #
    # def get_ch2frequency(self):
    #     return float(self.interface.query("C1f?"))*1e6
    #
    # def set_ch2frequency(self, value):
    #     self.interface.write("C1f{:f}".format(value/1e6))
    #
    # def get_ch2power(self):
    #     return float(self.interface.query("C1W?"))
    #
    # def set_ch2power(self, value):
    #     self.interface.write("C1W{:f}".format(value))
    #
    # def get_ch2output(self):
    #     return int(self.interface.query("C1r?".format))
    #
    # def set_ch2output(self, value):
    #     self.interface.write("C1r{:d}".format(value))
