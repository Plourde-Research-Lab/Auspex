from .instrument import Instrument, VisaInterface
from types import MethodType


class Attenuator(Instrument):
    """BBN 3 Channel Instrument"""

    NUM_CHANNELS = 3

    def __init__(self, name, resource_name):
        super(Attenuator, self).__init__(name, resource_name, interface_type="VISA")
        self.interface._resource.baud_rate = 115200
        self.interface._resource.read_termination = u"\r\n"
        self.interface._resource.write_termination = u"\n"

        #Override query to look for ``end``
        def query(self, query_string):
            val = self._resource.query(query_string)
            assert self.read() == "END"
            return val

        self.interface.query = MethodType(query, self.interface, VisaInterface)

    @classmethod
    def channel_check(cls, chan):
        """ Assert the channel requested is feasbile """
        assert chan > 0 and chan <= cls.NUM_CHANNELS, "Invalid channel requested: channel ({:d}) must be between 1 and {:d}".format(chan, cls.NUM_CHANNELS)

    def get_attenuation(self, chan):
        Attenuator.channel_check(chan)
        return float(self.interface.query("GET {:d}".format(chan)))

    def set_attenuation(self, chan, val):
        Attenuator.channel_check(chan)
        self.interface.write("SET {:d} {:.1f}".format(chan, val))
        assert self.interface.read() == "Setting channel {:d} to {:.2f}".format(chan, val)
        assert self.interface.read() == "END"