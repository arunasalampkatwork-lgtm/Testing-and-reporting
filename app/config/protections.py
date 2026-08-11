PROTECTIONS = {

    "50": {
        "name": "Overcurrent Protection",

        "settings": [
            {
                "key": "pms",
                "label": "PMS",
                "type": "text",
                "unit": "×In",
            },
            {
                "key": "time",
                "label": "Time",
                "type": "text",
                "unit": "",
            },
            {
                "key": "tms",
                "label": "TMS",
                "type": "text",
                "unit": "",
            },
            {
                "key": "curve",
                "label": "Curve",
                "type": "text",
                "unit": "",
            },
        ],

        "measurements": {
            "type": "phase",
            "phases": [
                "R",
                "Y",
                "B",
            ],
            "fields": [
                {
                    "key": "injected_current",
                    "label": "Injected Current",
                    "type": "text",
                    "unit": "A",
                },
                {
                    "key": "trip_time",
                    "label": "Trip Time",
                    "type": "text",
                    "unit": "ms",
                },
            ],
        },
    },


    "50G": {
        "name": "Earth Fault Protection",

        "settings": [
            {
                "key": "pms",
                "label": "PMS",
                "type": "text",
                "unit": "×In",
            },
            {
                "key": "time",
                "label": "Time",
                "type": "text",
                "unit": "",
            },
            {
                "key": "tms",
                "label": "TMS",
                "type": "text",
                "unit": "",
            },
            {
                "key": "curve",
                "label": "Curve",
                "type": "text",
                "unit": "",
            },
        ],

        "measurements": {
            "type": "phase",
            "phases": [
                "R",
                "Y",
                "B",
            ],
            "fields": [
                {
                    "key": "injected_current",
                    "label": "Injected Current",
                    "type": "text",
                    "unit": "A",
                },
                {
                    "key": "trip_time",
                    "label": "Trip Time",
                    "type": "text",
                    "unit": "ms",
                },
            ],
        },
    },


    "49": {
        "name": "Thermal Overload Protection",

        "settings": [
            {
                "key": "flc",
                "label": "FLC",
                "type": "text",
                "unit": "A",
            },
            {
                "key": "i",
                "label": "I",
                "type": "text",
                "unit": "× Itheta",
            },
            {
                "key": "itheta",
                "label": "Itheta",
                "type": "text",
                "unit": "",
            },
            {
                "key": "k",
                "label": "K",
                "type": "text",
                "unit": "",
            },
            {
                "key": "tauh_heating",
                "label": "Tauh Heating Constant",
                "type": "text",
                "unit": "",
            },
            {
                "key": "tauh_cooling",
                "label": "Tauh Cooling Constant",
                "type": "text",
                "unit": "",
            },
            {
                "key": "tauh_starting",
                "label": "Tauh Starting Constant",
                "type": "text",
                "unit": "",
            },
            {
                "key": "time",
                "label": "Time",
                "type": "text",
                "unit": "",
            },
            {
                "key": "tms",
                "label": "TMS",
                "type": "text",
                "unit": "",
            },
            {
                "key": "curve",
                "label": "Curve",
                "type": "text",
                "unit": "",
            },
        ],

        "measurements": {
            "type": "phase",
            "phases": [
                "R",
                "Y",
                "B",
            ],
            "fields": [
                {
                    "key": "injected_current",
                    "label": "Injected Current",
                    "type": "text",
                    "unit": "A",
                },
                {
                    "key": "trip_time",
                    "label": "Trip Time",
                    "type": "text",
                    "unit": "s",
                },
            ],
        },
    },
}


def get_protection(code):

    return PROTECTIONS.get(code)


def get_protection_codes():

    return list(PROTECTIONS.keys())