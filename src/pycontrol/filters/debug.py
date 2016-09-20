# Copyright 2016 Raytheon BBN Technologies
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0

import asyncio, concurrent
import numpy as np
from pycontrol.filters.filter import Filter
from pycontrol.stream import InputConnector, OutputConnector
from pycontrol.log import logger

class Print(Filter):
    """Debug printer that prints data comming through filter"""

    sink = InputConnector()

    def __init__(self, *args, **kwargs):
        super(Print, self).__init__(*args, **kwargs)

    async def process_data(self, data):

        logger.debug('%s "%s" received points: %s', self.__class__.__name__, self.name, data)

class Passthrough(Filter):
    sink   = InputConnector()
    source = OutputConnector()

    def __init__(self, *args, **kwargs):
        super(Passthrough, self).__init__(*args, **kwargs)

    async def process_data(self, data):
        for os in self.source.output_streams:
            await os.push(data)
