# Copyright 2016 Raytheon BBN Technologies
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0

__all__ = ['DPO72004C', 'PPG4001']

from auspex.log import logger
from .instrument import SCPIInstrument, StringCommand, FloatCommand, IntCommand
import numpy as np

class DPO72004C(SCPIInstrument):
    """Tektronix DPO72004C Oscilloscope"""
    encoding   = StringCommand(get_string="DAT:ENC;", set_string="DAT:ENC {:s};",
                        allowed_values=["ASCI","RIB","RPB","FPB","SRI","SRP","SFP"])
    byte_depth = IntCommand(get_string="WFMOutpre:BYT_Nr?;",
                            set_string="WFMOutpre:BYT_Nr {:d};", allowed_values=[1,2,4,8])
    data_start = IntCommand(get_string="DAT:STAR?;", set_string="DAT:STAR {:d};")
    data_stop  = IntCommand(get_string="DAT:STOP?;", set_string="DAT:STOP {:d};")

    fast_frame      = StringCommand(get_string="HORizontal:FASTframe:STATE?;", set_string="HORizontal:FASTframe:STATE {:s};",
                       value_map       = {True: '1', False: '0'})
    num_fast_frames = IntCommand(get_string="HOR:FAST:COUN?;", set_string="HOR:FAST:COUN {:d};")

    preamble = StringCommand(get_string="WFMOutpre?;") # Curve preamble

    record_length   = IntCommand(get_string="HOR:ACQLENGTH?;")
    record_duration = FloatCommand(get_string="HOR:ACQDURATION?;")

    def __init__(self, resource_name, *args, **kwargs):
        resource_name += "::4000::SOCKET" #user guide recommends HiSLIP protocol
        super(DPO72004C, self).__init__(resource_name, *args, **kwargs)
        self.name = "Tektronix DPO72004C Oscilloscope"
        self.interface._resource.read_termination = u"\n"

    def clear(self):
        self.interface.write("CLEAR ALL;")

    def snap(self):
        """Sets the start and stop points to the the current front panel display.
        This doesn't actually seem to work, strangely."""
        self.interface.write("DAT SNAp;")

    def get_curve(self, channel=1, byte_depth=2):
        channel_string = "CH{:d}".format(channel)
        self.interface.write("DAT:SOU {:s};".format(channel_string))
        self.source_channel = 1
        self.encoding = "SRI" # Signed ints

        record_length = self.record_length
        self.data_start = 1
        self.data_stop  = record_length

        self.byte_depth = byte_depth
        strf_from_depth = {1: 'b', 2: 'h', 4: 'l', 8: 'q'}

        curve = self.interface.query_binary_values("CURVe?;", datatype=strf_from_depth[byte_depth])
        scale = self.interface.value('WFMO:YMU?;')
        offset = self.interface.value('WFMO:YOF?;')
        curve = (curve - offset)*scale
        if self.fast_frame:
            curve.resize((self.num_fast_frames, record_length))
        return curve

    def get_timebase(self):
        return np.linspace(0, self.record_duration, self.record_length)

    def get_fastaq_curve(self, channel=1):
        channel_string = "CH{:d}".format(channel)
        self.interface.write("DAT:SOU {:s};".format(channel_string))
        self.source_channel = 1
        self.encoding = "SRP" # Unsigned ints
        self.byte_depth  = 8
        self.data_start = 1
        self.data_stop  = self.record_length
        curve = self.interface.query_binary_values("CURVe?;", datatype='Q').reshape((1000,252))
        return curve

    def get_math_curve(self, channel=1):
        pass


class PPG4001(SCPIInstrument):
    """Tektronix PPG4001 Pattern Generator"""
    
    amplitude      = FloatCommand(get_string=":VOLTage:POS?;",
                                  set_string=":VOLTage:POS {:.3f};")
    
    offset         = FloatCommand(get_string=":VOLTage:OFFSet?;",
                                  set_string=":VOLTage:OFFSet {:.3f};")
    
    polarity       = StringCommand(get_string=":OUTPut1:POLarity?",
                                   set_string=":OUTPut1:POLarity {:s}",
                                   allowed_values=['NORM', 'INV'])
    
    pattern_length = IntCommand(get_string=":DIG:PATT:LENG?;", 
                                set_string=":DIG:PATT:LENG {:d};")
    
    pattern_rate   = FloatCommand(get_string=":FREQ", set_string=":FREQ {:.5f}")
    
    
    
    def __init__(self, resource_name, *args, **kwargs):
        super(PPG4001, self).__init__(resource_name, *args, **kwargs)
        self.name = "Tektronix PPG4001 Pattern Generator"
        self.interface._resource.read_termination = u"\n"   
        
        
    def dataStr(self, pulse,loc=1):
        '''Generate command string for pulse pattern'''
        length = len(pulse)
        return ':DIG1:PATT:DATA {:d},{:d},#{:d}{:d}{:s}'.format(
            loc,
            length,
            len(str(length)),
            length,
            "".join([str(int(x)) for x in pulse])
        )
    
    def load_pattern(self, pattern):
        '''Write pulse to PPG in 1024 bit blocks'''
        q,r = divmod(len(pattern),1024)
        for i in np.arange(q):
            self.interface.write(self.dataStr(pulse[(1024*i):1024*(i+1)], 
                                              loc=int(1024*i)+1))
        self.interface.write(self.dataStr(pulse[-1*r:], 
                                          loc=1024*q))
        
    def dataQuery(self, numBits, loc):
        '''Parse pulse pattern query'''
        res = self.interface.query(':DIG:PATT:DATA? {:d},{:d}'
                                   .format(loc, numBits)).strip()
        bits = res[int(res[1])+2:]
        return bits
    
    def read_pattern(self, numBits):
        '''Read pulse from PPG in 1024 bit blocks'''
        q,r = divmod(numBits,1024)
        ret = ""
        for i in np.arange(q):
            ret += self.dataQuery(1024, loc=int(1024*i)+1)
        ret += self.dataQuery(r, loc=1024*q)
        return ret