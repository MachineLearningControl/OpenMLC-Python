
Due = {"NAME": "Arduino Due",
       "SHORT_NAME": "due",
       "ANALOG_PINS": range(54, 68),
       "DIGITAL_PINS": range(0, 54),
       "PWM_PINS": (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13),
       "ANALOG_DEFAULT_RESOLUTION": 12}

Uno = {"NAME": "Arduino Uno",
       "SHORT_NAME": "uno", "ANALOG_PINS": range(14, 20),
       "DIGITAL_PINS": range(0, 14),
       "PWM_PINS": (3, 5, 6, 9, 10, 11),
       "ANALOG_DEFAULT_RESOLUTION": 10}

Mega = {"NAME": "Arduino Mega",
        "SHORT_NAME": "mega",
        "ANALOG_PINS": range(54, 70),
        "DIGITAL_PINS": range(0, 54),
        "PWM_PINS": range(2, 14),
        "ANALOG_DEFAULT_RESOLUTION": 10}

Leonardo = {"NAME": "Arduino Leonardo",
            "SHORT_NAME": "leonardo",
            "ANALOG_PINS": range(14, 20),
            "DIGITAL_PINS": range(0, 14),
            "PWM_PINS": (3, 5, 6, 9, 10, 11, 12, 13),
            "ANALOG_DEFAULT_RESOLUTION": 10}

types = [Due, Uno, Mega, Leonardo]
