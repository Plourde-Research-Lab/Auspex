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
    ch1output    = Command(get_string="C0h?", set_string="C0h{!s}",
                        value_map={True: '1', False: '0'})

    ch2frequency = FloatCommand(get_string="C1f?", set_string="C1f{:f}")
    ch2power     = FloatCommand(get_string="C1W?", set_string="C1W{:f}")
    ch2output    = Command(get_string="C1h?", set_string="C1h{!s}",
                        value_map={True: '1', False: '0'})

    freqsource  = StringCommand(scpi_string="x",
                          value_map={'INTERNAL 10MHz': '2',
                                     'INTERNAL 27MHz': '1',
                                     'EXTERNAL': '0'})

    def __init__(self, resource_name=None, *args, **kwargs):
        super(SynthHD, self).__init__(resource_name, *args, **kwargs)

    def connect(self, resource_name=None, interface_type="VISA"):
        if resource_name is not None:
            self.resource_name = resource_name

        # print(self.resource_name)
        super(SynthHD, self).connect(resource_name=resource_name, interface_type=interface_type)
        self.interface._resource.read_termination = u"\n"
        self.interface._resource.write_termination = u"\n"
        # self.interface._resource.timeout = 3000 #seem to have trouble timing out on first query sometimes

        # Set External 10MHz Reference
        self.interface.write('*10x0')

        # Turn on
        self.interface.write("C0E1r1C1E1r1")
