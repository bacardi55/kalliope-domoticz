import logging
import imp

from kalliope.core.NeuronModule import NeuronModule, InvalidParameterException

logging.basicConfig()
logger = logging.getLogger("kalliope")

class Domoticz (NeuronModule):
    def __init__(self, **kwargs):
        super(Domoticz, self).__init__(**kwargs)

        # Get parameters form the neuron
        self.configuration = {
            'action': kwargs.get('action', None),
            'action_value': kwargs.get('action_value', None),
            'host': kwargs.get('host', None),
            # Because Kalliope receive arguments as string
            'ssl_verify': False if kwargs.get('ssl_verify', True) == 'False' else True,
            'device': kwargs.get('device', None)
        }
        logger.debug(self.configuration)

        message = {
            "status": "KO",
            "devices": []
        }

        # Check parameters:
        if self._is_parameters_ok():
            self.init_pymoticz()
            if self.configuration['action'] == 'get_device':
                message['devices'] = self._get_device(self.configuration['device'])
                message['status'] = "OK"
                logger.debug(message['devices'])
            elif self.configuration['action'] == 'get_scene':
                pass
            elif self.configuration['action'] == 'set_scene':
                pass
            elif self.configuration['action'] == 'set_scene_on':
                pass
            elif self.configuration['action'] == 'set_scene_off':
                pass
            elif self.configuration['action'] == 'set_switch':
                message['status'] = self._set_light(self.configuration['device'], self.configuration['action_value'])
                pass

        self.say(message)

    def init_pymoticz(self):
        pymoticzFile = imp.load_source("Pymoticz", "resources/neurons/domoticz/pymoticz.py")
        self.p = pymoticzFile.Pymoticz(self.configuration['host'], ssl_verify=self.configuration['ssl_verify'])

    def _get_device(self, device_id=None):
        devices = []
        #devices = self.p.get_device
        if device_id is None:
            response = self.p.list()
            devices = response['result']
        else:
            devices = [self.p.get_device(device_id)]

        #logger.debug(devices)
        return devices

    def _set_light(self, device, action):
        if action == "on":
            response = self.p.turn_on(device)
        elif action == "off":
            response = self.p.turn_off(device)

        return response['status']

    def _is_parameters_ok(self):
        """
        Check if received parameters are ok to perform operations in the neuron
        :return: true if parameters are ok, raise an exception otherwise
        .. raises:: InvalidParameterException
        """
        if self.configuration['host'] is None:
            raise InvalidParameterException("Domoticz host is required")

        if self.configuration['action'] is None:
            raise InvalidParameterException("Domoticz action is required")

        if self.configuration['action'] in ['get_device', 'set_switch'] and self.configuration['device'] is None:
            raise InvalidParameterException("Domoticz device is required for the action %s" % self.configuration['action'])

        logger.debug(self.configuration)
        if self.configuration['action'] in ['set_switch'] and self.configuration['action_value'] is None:
            raise InvalidParameterException("Domoticz action_value is required for the action %s" % self.configuration['action'])

        return True

