"""Constants for the edilkamin integration."""
import logging

from homeassistant.components.climate import (
    FAN_AUTO
)
DOMAIN = "edilkamin"
LOGGER = logging.getLogger(__package__)

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
    FAN_SPEED_1: FAN_MODE_1,
    FAN_SPEED_2: FAN_MODE_2,
    FAN_SPEED_3: FAN_MODE_3,
    FAN_SPEED_4: FAN_MODE_4,
    FAN_SPEED_5: FAN_MODE_5,
    FAN_SPEED_AUTO: FAN_AUTO
}

FAN_MODES = [FAN_MODE_1, FAN_MODE_2, FAN_MODE_3,
             FAN_MODE_4, FAN_MODE_5, FAN_AUTO]

FAN_SPEED_PERCENTAGE = {
    0: 0,
    1: 20,
    2: 40,
    3: 60,
    4: 80,
    5: 100
}

FAN_PERCENTAGE_SPEED = {
    0: 0,
    20: 1,
    40: 2,
    60: 3,
    80: 4,
    100: 5
}
