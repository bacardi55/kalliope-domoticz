# kalliope-domoticz

A neuron to leverage [domoticz](https://www.domoticz.com) API.

## Synopsis

Domoticz is a domotic tool to manage your different devices at home. It is extremely powerful and I use it manage some component via zwave.


**This module is not stable and I'm only starting developing it. Also I don't have a lot of z-wave devices so my tests are not exhaustive**
That being said, feel free to test and help me improve this module.

For now, [this sample brain file](https://github.com/bacardi55/kalliope-domoticz/blob/master/samples/brain_fr.yml) act as documentation 

What the neuron can do:

- Request device data (eg: Temp / Lux sensor) (by device id)
- set light switch on/off (by device id)


Todo:

- Get / set scenes
- …

## Installation

  ```
  kalliope install --git-url https://github.com/bacardi55/kalliope-domoticz.git
  ```


* [my posts about kalliope](http://bacardi55.org/en/term/kalliope) 
* [A blog post about this neuron](http://bacardi55.org/en/blog/2017/entering-domotic-game)

