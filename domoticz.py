import logging

from kalliope.core.NeuronModule import NeuronModule, InvalidParameterException

#import sys
#import os
#sys.path.append(os.getcwd())
#from . import Pymoticz


logging.basicConfig()
logger = logging.getLogger("kalliope")

class Domoticz (NeuronModule):
    def __init__(self, **kwargs):
        super(Domoticz, self).__init__(**kwargs)

        # Get parameters form the neuron
        self.configuration = {
            'host': kwargs.get('host', None)
        }

        message = {}

        # Check parameters:
        if self._is_parameters_ok():
            p = Pymoticz(self.configuration['host'])

        message['p'] = p
        #self.say(message)


    def _is_parameters_ok(self):
        """
        Check if received parameters are ok to perform operations in the neuron
        :return: true if parameters are ok, raise an exception otherwise
        .. raises:: InvalidParameterException
        """
        if self.configuration['host'] is None:
            raise InvalidParameterException("Domoticz host is required")


        return True

