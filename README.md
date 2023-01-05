# ha-edilkamin

Edilkamin The Mind custom integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

This component provides custom integration with Edilkamin pellet stoves and The Mind Wifi module. It was tested with a 2022 Lena stove and may not work at 100% with other models. 

Based on the unofficial Python library [edilkamin.py](https://github.com/AndreMiras/edilkamin.py)

## How to install
You can use HACS to install this integration as custom repository

If you are not using HACS, you must copy `edilkamin` into your `custom_components` folder on HA

## Configuration

The Stove should be discovered automatically with DHCP discovery.

If not, add an instance of `Edilkamin Stove` using the UI in the integration section. You will need to provide the username and password used to register the stove in the Mind smartphone app. You also need to provide the Wifi MAC Address of the stove, which can be found in the Mind App, `Main Menu > Settings > Software > MQTT MAC`

## Main features

- Climate entity for the stove, with manual power control and manual fan control
- DHCP discovery or manual entry with MAC Address
- Auxiliary fans control (with fan entities)
- Auto mode
- Stove operational mode
- Display current power level
- Coordinator for all data upgrades
- Switch entities for silent mode, standby mode, airkare
- Sensors entities for the running time and number of power ons

## Issues / To-Do

- Issues with the refresh of the sensors
- More tests needed for the alarm sensor
- Create airkare switch entity only if feature is available

## Disclaimer
- The API calls come from the reverse envineering of the Android app, and are not guaranteed to work in the long term
- Consider doing changes that suite your needs
- Use at your own risk

## Thanks to
- @AndreMiras for reverse engineering the Android app and providing the Python librairy for most of the API calls, and also for the initial component code
- @shisva for its contributions and testing
