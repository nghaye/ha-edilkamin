# ha-edilkamin

Edilkamin The Mind custom integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

This component provides custom integration with Edilkamin pellet stoves and The Mind Wifi module. It was tested with a 2022 Lena stove and may not work at 100% with other models. 

Based on the unofficial Python library [edilkamin.py](https://github.com/AndreMiras/edilkamin.py)

## How to install
You can use HACS to install this integration as custom repository.

If you are not using HACS, you must copy `edilkamin` into your `custom_components` folder on HA.

## Configuration

The Stove should be discovered automatically with DHCP discovery.

If not, add an instance of `Edilkamin Stove` using the UI in the integration section. You will need to provide the username and password used to register the stove in the Mind smartphone app. You also need to provide the Wifi MAC Address of the stove, which can be found in the Mind App, `Main Menu > Settings > Software > MQTT MAC`

## Main features

- DHCP discovery or manual entry with Wifi MAC Address
- Climate entity for the stove, with the following features :
  - Manual/auto power control 
  - Manual/auto fan control
  - Temperature measurement from the remote
  - (extra attribute) Operationnal mode
  - (extra attribute) Current power level
- Fan entities for each auxiliary fan
- Switch entities
  - Silent mode
  - Standby mode
  - Airkare
- Sensor entities
  - Number of power ons
  - Running time
  - Current alarm
  - Last alarm 

## Issues / To-Do

- More tests needed for the alarm sensor, needs to map the different error codes and messages
- Create airkare switch entity only if feature is available

## Disclaimer
- The API calls come from the reverse envineering of the Android app, and are not guaranteed to work in the long term
- Consider doing changes that suite your needs
- Use at your own risk

## Thanks to
- @AndreMiras for reverse engineering the Android app and providing the Python librairy for most of the API calls, and also for the initial component code
- @shisva for its contributions and testing
