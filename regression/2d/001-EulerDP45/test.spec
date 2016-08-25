{    
    "runs": [
        {
            "project": "heat_1_100e_big.json",
            "postfix": "",
            "params": ""
        },
        {
            "project": "heat_1_100e_small.json",
            "postfix": "",
            "params": ""
        },
        {
            "project": "heat_1_100d.json",
            "postfix": "",
            "params": ""
        }       
    ],
    "tests":
        [
            {
            "run1": "heat_1_100e_small",
            "run2": "heat_1_100e_big",
            "timestamp1": "0.10000000",
            "timestamp2": "0.10001000",
            "tolerances":
                {
                    "max": 2.0, 
                    "ave": 2.0
                }
            },
            {
            "run1": "heat_1_100e_small",
            "run2": "heat_1_100d",
            "timestamp1": "0.10000000",
            "timestamp2": "0.10001950",
            "tolerances":
                {
                    "max": 2.0, 
                    "ave": 2.0
                }
            },
            {
            "run1": "heat_1_100e_big",
            "run2": "heat_1_100d",
            "timestamp1": "0.10001000",
            "timestamp2": "0.10001950",
            "tolerances":
                {
                    "max": 2.0, 
                    "ave": 2.0
                }
            }
       ]
}