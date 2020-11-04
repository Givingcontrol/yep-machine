# Yep Machine

Smart fucking machine [video](https://twitter.com/yepdev_/status/1321421143283294208)

## Project features

- Fully customizable thrust time, speed, ramp up/down and patterns (for now only time changeable in UI)
- Moves generated based on position graphs generated in Python
- Limit switches handling
- Automatic calibration
- Visible machine state

## What this repo does

- Controlling stepper motor driver
- Handling two limit switches
- Running commands and waves provided by server over websocket
- Reporting machine status to server over websocket

## Architecture

This is just Raspberry Pi code, it needs other modules to function:

- [yep-server](https://github.com/yep-dev/yep-server) - generating moves waves, synchronizing state
- [yep-app](https://github.com/yep-dev/yep-app) - UI, control panel

![architecture](https://github.com/yep-dev/yep-machine/blob/master/docs/architecture.png?raw=true)

## Installation

- *Disable remote GPIO*
- Install docker and docker-compose


## Hardware

![architecture](https://github.com/yep-dev/yep-machine/blob/master/docs/hardware.png?raw=true)

Main parts list:

| Name                   | Pcs | price |link                                                       |notes
|---                     |---  |---    |---                                                        |---                                           
|Raspberry Pi 4 2GB      | 1   | $42   |[link](https://pl.aliexpress.com/item/32838484861.html)    |Only version 4 has sufficient GPIO performance
|Stepper motor and driver| 1   | $74   |[link](https://pl.aliexpress.com/item/4000071371127.html)  |Other, cheaper stepper motors and drivers can be used, but the software is tuned for this one
|Limit switch            | 2   | $1    |[link](https://pl.aliexpress.com/item/32966619156.html)    |
|Pulley kit              | 1   | $5    |[link](https://pl.aliexpress.com/item/4000091123800.html)  |
|Linear rail kit         | 1   | $8    |    

Wiring schematic (use Raspberry Pi 4):

![architecture](https://github.com/yep-dev/yep-machine/blob/master/docs/schematic.png?raw=true)
