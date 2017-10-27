# Copyright 2016 Raytheon BBN Technologies
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0

__all__ = ['HittiteHMCT2100']

from .instrument import SCPIInstrument, StringCommand, FloatCommand, IntCommand, is_valid_ipv4
from auspex.log import logger
import time
import numpy as np
import socket

class HittiteHMCT2100(SCPIInstrument):
    """HittiteHMCT2100 microwave source"""
    instrument_type = "Microwave Source"

    frequency = FloatCommand(scpi_string="freq")
    power     = FloatCommand(scpi_string="power")
    phase     = FloatCommand(scpi_string="phase")

    output    = StringCommand(scpi_string="output", value_map={True: 'on', False: 'off'})

    def __init__(self, resource_name=None, *args, **kwargs):
        #If we only have an IP address then tack on the raw socket port to the VISA resource string
        super(HittiteHMCT2100, self).__init__(resource_name, *args, **kwargs)

    def connect(self, resource_name=None, interface_type="VISA"):
        if resource_name is not None:
            self.resource_name = resource_name
        if is_valid_ipv4(self.resource_name):
            if "::5025::SOCKET" not in self.resource_name:
                self.resource_name += "::5025::SOCKET"
        print(self.resource_name)
        super(HMCT2100, self).connect(resource_name=resource_name, interface_type=interface_type)
        self.interface._resource.read_termination = u"\n"
        self.interface._resource.write_termination = u"\n"
        self.interface._resource.timeout = 3000 #seem to have trouble timing out on first query sometimes

    def set_all(self, settings):
        super(HittiteHMCT2100, self).set_all(settings)
