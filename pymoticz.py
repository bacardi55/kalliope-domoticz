#!/usr/bin/env python
"""Usage:
    pymoticz list [--host=<host>] [--names|--idx] [--scenes]
    pymoticz status <id> [--host=<host>] [--scenes]
    pymoticz on <id> [--host=<host>] [--scenes]
    pymoticz off <id> [--host=<host>] [--scenes]
    pymoticz dim <id> <level> [--host=<host>]
    pymoticz getSun [--host=<host>]
    pymoticz addSwitch
    pymoticz listTimers <id>
    pymoticz addTimer <id> <time> <cmd>
    pymoticz addDummy <type>
    pymoticz log <id>
    pymoticz rename <id> <name>
    pymoticz delete <id>
    pymoticz setCounter <id> <value>
    pymoticz changeCounterType <id> <type>
    pymoticz increment <id>
"""
import requests
import json

__all__ = [ 'Pymoticz' ]
__version__ = '0.1'

#dummyTypes :[Type,SubType, friendly name]
dummyTypes = {
    1 : ['General','Pressure', 'pressure'],
    2 : ['General','Percentage','percentage'],
    3 : ['P1 Smart Meter','Gas','gas'],
    4 : ['General','Voltage','voltage'],
    5 : ['General','Text','text'],
    6 : ['Lighting 2','AC','switch'],
    7 : ['General','Alert','alert'],
    8 : ['Thermostat','SetPoint','thermostat'],
    9 : ['Current','CM113, Electrisave','current'],
    10 : ['General','Sound Level','sound level'],
    11 : ['General','Barometer','barometer'],
    12 : ['General','Visibility','visibility'],
    13 : ['General','Distance','distance'],
    14 : ['General','Counter Incremental','counter'],
    15 : ['General','Soil Moisture','soil moisture'],
    16 : ['General','Leaf Wetness','leaf wetness'],
    17 : ['General','Thermostat Clock','thermostat clock'],
    18 : ['General','kWh','power usage'],
    80 : ['Temp','THR128/138, THC138','temperature'],
    241 : ['Lighting Limitless/Applamp','RGB','rgb'],
    250 : ['P1 Smart Meter','Energy','p1']
    }


counterTypes = {
    0 : 'energy',
    1 : 'gas',
    2 : 'water',
    3 : 'coutner',
    4 : 'energy generated'
    }

def printResponse (_response, _OK, _ERR):
    if _response['status'] == 'OK':
        print (_OK)
    else:
        print (_ERR)


class Pymoticz:
    DIMMER = u'Dimmer'
    ON_OFF = u'On/Off'
    SWITCH_TYPES=[ DIMMER, ON_OFF ]
    def __init__(self, domoticz_host='127.0.0.1:8080', ssl_verify=True):
        if domoticz_host.startswith('http') is False:
            domoticz_host = 'http://' + domoticz_host
        self.host = domoticz_host
        self.ssl_verify = ssl_verify

    def getSensorID (self,type):
        for id, tuples in dummyTypes.items():
            if tuples[2] == type:
                return id

        return 0

    def _request(self, url):
        r=requests.get(url, verify = self.ssl_verify)

        if r.status_code == 200:
            return json.loads(r.text)
        else:
            raise

    def list_hard_idx(self):
        l=self.list_hard()
        return ["%s\t%s" % (device['idx'], device['Name']) for device in l['result']]

    def list_hard(self):
        url='%s/json.htm?type=hardware' % self.host
        return self._request(url)

    def data_idx(self,_id):
        url='%s/json.htm?type=devices&rid=%s' %(self.host, _id)
        return self._request(url)

    def list_names(self):
        l=self.list()
        return [device['Name'] for device in l['result']]

    def list_idx(self):
        l=self.list()
        return ["%s\t%s (%s-%s)" % (device['idx'], device['Name'], device['Type'], device['SubType']) for device in l['result']]

    def list(self):
        url='%s/json.htm?type=devices&used=true' % self.host
        return self._request(url)

    def list_scenes(self):
        url='%s/json.htm?type=scenes&used=true' % self.host
        return self._request(url)

    def list_scenes_names(self):
        l=self.list_scenes()
        return [device['Name'] for device in l['result']]

    def list_scenes_idx(self):
        l=self.list_scenes()
        return ["%s\t%s" % (device['idx'], device['Name']) for device in l['result']]

    def turn_on(self, _id):
        url='%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=On' % (self.host, _id)
        return self._request(url)

    def turn_off(self, _id):
        url='%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=Off&level=0' % (self.host, _id)
        return self._request(url)

    def turn_on_scene(self, _id):
        url='%s/json.htm?type=command&param=switchscene&idx=%s&switchcmd=On' % (self.host, _id)
        return self._request(url)

    def turn_off_scene(self, _id):
        url='%s/json.htm?type=command&param=switchscene&idx=%s&switchcmd=Off&level=0' % (self.host, _id)
        return self._request(url)

    def dim(self, _id, level):
        d=self.get_device(_id)
        if d is None:
            return 'No device with that id.'

        max_dim=d['MaxDimLevel']
        if int(level) > max_dim or int(level) < 0:
            return 'Level has to be in the range 0 to %d' % max_dim
        url='%s/json.htm?type=command&param=switchlight&idx=%s&switchcmd=Set Level&level=%s' % (self.host, _id, level)
        return self._request(url)

    def set_counter (self, _id, _value):
        url='%s/json.htm?type=command&param=udevice&idx=%s&nvalue=%s' % (self.host, _id, _value)
        response = self._request(url)
        return response

    def increment_counter (self, _id):
        l=self.data_idx(_id)
        actualValue = [device['Data'] for device in l['result']][0]
        actualValue = int (actualValue)
        actualValue+=1
        url='%s/json.htm?type=command&param=udevice&idx=%s&nvalue=%s' % (self.host, _id, actualValue)
        response = self._request(url)
        printResponse(response, "value of device %s changed to %s" % (_id, actualValue), "ERROR")
        return response


    def get_device(self, _id):
        l=self.list()
        try:
            device=[i for i in l['result'] if i['idx'] == u'%s' % _id][0]
        except:
            return None
        return device

    def get_scene(self, _id):
        l=self.list_scenes()
        try:
            scene=[i for i in l['result'] if i['idx'] == u'%s' % _id][0]
        except:
            return None
        return scene

    def get_light_status(self, _id):
        light = self.get_device(_id)
        if light is None:
            return 'No device with that id.'
        if light['SwitchType'] not in self.SWITCH_TYPES:
            return 'Not a light switch'
        elif light['SwitchType'] == self.DIMMER:
            return "%s\t%s" % (light['Status'], light['Level'])
        elif light['SwitchType'] == self.ON_OFF:
            return "%s\t%s" % (light['Status'], 100)

    def get_scene_status(self, _id):
        scene = self.get_scene(_id)
        if scene is None:
            return 'No scene/group with that id.'
        else:
            return scene['Status']

    def get_sun(self):
        url='%s/json.htm?type=command&param=getSunRiseSet' % self.host
        response = self._request(url)
        if response['status'] == 'ERR':
            return "ERROR can't get sun informations"
        else:
            return "%s\t%s" % (response['Sunrise'], response['Sunset'])

    def get_logs(self, _id):
        url='%s/json.htm?type=textlog&idx=%s' % (self.host, _id)
        response = self._request(url)
        if 'result' in response:
            l=response
            return ["%s\t%s" % (device['Date'], device['Data']) for device in l['result']]
        else:
            return 0

    def rename (self, _id, _name):
        url='%s/json.htm?type=command&param=renamedevice&idx=%s&name=%s' % (self.host, _id, _name)
        response = self._request(url)
        return response

    def get_timers(self, _id):
        url='%s/json.htm?type=timers&idx=%s' % (self.host, _id)
        response = self._request(url)
        if 'result' in response:
            l=response
            return ["%s\t%s\t%s" % (device['idx'], device['Time'], device['Cmd']) for device in l['result']]
        else:
            return 0

    def add_timer(self, _id, time, cmd):
        hour=time.split(":")[0]
        min=time.split(":")[1]
        if cmd.lower()== 'on' :
            cmd = 0
        else :
            cmd = 1
        url='%s/json.htm?type=command&param=addtimer&idx=%s&active=true&timertype=2&date=&hour=%s&min=%s&randomness=false&command=%s&level=100&hue=0&days=128' % (self.host, _id, hour, min, cmd)
        response = self._request(url)
        return response


    def delete (self, _id):
        url='%s/json.htm?type=deletedevice&idx=%s' % (self.host, _id)
        response = self._request(url)
        return response

    def get_dummy_id(self):
        l=self.list_hard()
        for device in l['result'] :
           if device['Type'] == 15 :
              return device['idx']
        return 0

    def get_dummy_switch(self):
        url='%s/json.htm?type=devices&filter=light&used=false&order=LastUpdate' % self.host
        l =self._request(url)
        for device in l['result'] :
            if device['Name'] == 'Unknown' :
                return device['idx']
        return 0

    def get_dummy_device_id(self, id):
        url='%s/json.htm?type=devices&filter=all&used=false&order=Name' % self.host
        l =self._request(url)
        for device in l['result'] :
            if device ['SubType'] == dummyTypes[id][1] :
                if device['Name'] == 'Unknown' :
                    return device['idx']

        return 0

    def addVirtualSensor (self, type):
       l=self.list_hard()
       dummyId=self.get_dummy_id()
       if dummyId != 0 :
            url='%s/json.htm?type=createvirtualsensor&idx=%s&sensortype=%s' % (self.host, dummyId, type)
            response = self._request(url)
            # we enable the dummy
            dummySwID=self.get_dummy_device_id(type)
            if dummySwID != 0 :
                url='%s/json.htm?type=setused&idx=%s&name=dummy%s&used=true&maindeviceidx=' % (self.host, dummySwID, dummySwID)
                response = self._request(url)
                return dummySwID
            else :
                print ("ERROR")
       else :
           print ("ERROR : no dummy device found, create one before adding virtual switch")
           return 0



if __name__ == '__main__':
    from docopt import docopt
    from pprint import pprint
    args=docopt(__doc__, version=__version__)

    p=None
    if args['--host']:
        p=Pymoticz(args['--host'])
    else:
        p=Pymoticz()


    if args['list']:
        if args['--scenes']:
            if args['--names']:
                print('\n'.join(p.list_scenes_names()))
            elif args['--idx']:
                print('\n'.join(p.list_scenes_idx()))
            else:
                pprint(p.list_scenes())
        else:
            if args['--names']:
                print('\n'.join(p.list_names()))
            if args['--idx']:
                print('\n'.join(p.list_idx()))
            else:
                pprint(p.list())

    elif args['status']:
        if args['--scenes']:
            response = p.get_scene_status(args['<id>'])
        else:
            response = p.get_light_status(args['<id>'])
        print(response)

    elif args['on']:
        if args['--scenes']:
            response = p.turn_on_scene(args['<id>'])
        else:
            response = p.turn_on(args['<id>'])
    elif args['off']:
        if args['--scenes']:
            response = p.turn_off_scene(args['<id>'])
        else:
            response = p.turn_off(args['<id>'])
    elif args['dim']:
        response = p.dim(args['<id>'], args['<level>'])
        print (response)


    elif args['addDummy']:
        sensorID = p.getSensorID(args['<type>'])
        if sensorID == 0 :
            print ("%s is not a valid type. Choose :" % args['<type>'])
            for x in dummyTypes.viewvalues() :
                print (x[2])
        else :

            response = p.addVirtualSensor(sensorID)
            if response != 0 :
                print ("dummy device %s created" %response)
            else :
                print ("error with dummy device creation")


    elif args['getSun']:
        response = p.get_sun()
        print(response)

    elif args['listTimers']:
        if (p.get_timers(args['<id>'])) == 0 :
            print ("no timers configured for this device")
        else :
            print ("0 = ON, 1 = OFF")
            print ('idTimer\ttime\tcmd')
            print('\n'.join(p.get_timers(args['<id>'])))

    elif args['addTimer']:
        response = p.add_timer(args['<id>'], args['<time>'], args['<cmd>'])
        print (response)

    elif args['delete']:
        response = p.delete(args['<id>'])
        print ("OK, device %s deleted" % (args['<id>']))

    elif args['setCounter']:
        response = p.set_counter(args['<id>'], args['<value>'])
        printResponse(response,  "OK: device %s set to %s" % (args['<id>'],  args['<value>']), "ERROR: can't update the device")
        #print response

    elif args['increment']:
        response = p.increment_counter(args['<id>'])
        #print (response)

    elif args['rename']:
        response = p.rename(args['<id>'], args['<name>'])
        print ("OK, device %s renamed to %s" % (args['<id>'], args['<name>']))

    elif args ['log']:
        device = args['<id>']
        response = p.get_logs(args['<id>'])
        if response == 0 :
            print ("ERROR : no device with this IDX")
        else :
            print ('\n'.join(p.get_logs(args['<id>'])))
