"""Constants for the edilkamin integration."""
import logging

DOMAIN = "edilkamin"
LOGGER = logging.getLogger(__package__)

from homeassistant.components.climate import (
    FAN_AUTO
)

FAN_SPEED_1 = 1
FAN_SPEED_2 = 2
FAN_SPEED_3 = 3
FAN_SPEED_4 = 4
FAN_SPEED_5 = 5
FAN_SPEED_AUTO = 6

FAN_MODE_1 = "20 %"
FAN_MODE_2 = "40 %"
FAN_MODE_3 = "60 %"
FAN_MODE_4 = "80 %"
FAN_MODE_5 = "100 %"

FAN_SPEED_TO_MODE = {
    FAN_SPEED_1 : FAN_MODE_1,
    FAN_SPEED_2 : FAN_MODE_2,
    FAN_SPEED_3 : FAN_MODE_3,
    FAN_SPEED_4 : FAN_MODE_4,
    FAN_SPEED_5 : FAN_MODE_5,
    FAN_SPEED_AUTO : FAN_AUTO
}

FAN_MODES = [FAN_MODE_1, FAN_MODE_2, FAN_MODE_3, FAN_MODE_4, FAN_MODE_5, FAN_AUTO]

PRESET_AUTO = "Auto"
PRESET_1 = "Manual P1"
PRESET_2 = "Manual P2"
PRESET_3 = "Manual P3"
PRESET_4 = "Manual P4"
PRESET_5 = "Manual P5"

PRESET_MODES = [PRESET_AUTO, PRESET_1, PRESET_2, PRESET_3, PRESET_4, PRESET_5]
PRESET_MODE_TO_POWER = {
    "Manual P1" : 1, 
    "Manual P2" : 2, 
    "Manual P3" : 3, 
    "Manual P4" : 4,
    "Manual P5" : 5
}

PREHEAT = "Preheat"
EXTINCTION = "Extinction"
OFF = "Off"
HEATING = "Heating"

OPERATIONAL_PHASE = {
    0 : OFF,
    1 : PREHEAT,
    2 : HEATING,
    3 : EXTINCTION,
    4 : OFF
}

FAN_SPEED_PERCENTAGE = {
    0 : 0,
    1 : 20,
    2 : 40,
    3 : 60,
    4 : 80,
    5 : 100
}

FAN_PERCENTAGE_SPEED = {
    0 : 0,
    20 : 1,
    40 : 2,
    60 : 3,
    80 : 4,
    100 : 5
}

# class StoveHVACAction() :
#     PREHEAT = "preheat"
#     EXTINCTION = "extinction"
#     OFF = "off"
#     HEATING = "heating"

#     OPERATIONNAL_PHASE = {
#         0 : OFF,
#         1 : PREHEAT,
#         2 : HEATING,
#         3 : EXTINCTION
#     }

#     def get_hvac_action(self, id) :
#         return self.OPERATIONNAL_PHASE[id]