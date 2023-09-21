import re


def is_valid_mac_address(str) -> bool:
    """Check if the given mac address is valid"""
    # Regex to check valid
    # MAC address
    regex = ("^([0-9A-Fa-f]{2}[:-])" +
             "{5}([0-9A-Fa-f]{2})|" +
             "([0-9a-fA-F]{4}\\." +
             "[0-9a-fA-F]{4}\\." +
             "[0-9a-fA-F]{4})|" +
             "[0-9a-fA-F]{12}$")

    # Compile the ReGex
    p = re.compile(regex)

    # If the string is empty
    # return false
    if (str is None):
        return False

    # Return if the string
    # matched the ReGex
    if (re.search(p, str)):
        return True
    else:
        return False
