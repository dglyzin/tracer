{    
    "runs": [
        {
            "project": "heat1d_1.json",
            "postfix": "",
            "params": ""
        },
        {
            "project": "heat1d_2.json",
            "postfix": "",
            "params": ""
        },
        {
            "project": "heat1d_4.json",
            "postfix": "",
            "params": ""
        },
        {
            "project": "heat1d_2.json",
            "postfix": "half",
            "params": "-finish 0.05"
        },
        {
            "project": "heat1d_2.json",
            "postfix": "full",
            "params": "-cont"
        }        
    ],
    "tests":
        [
            {
            "run1": "heat1d_1",
            "run2": "heat1d_2",
            "timestamp1": "0.10000000",
            "timestamp2": "0.10000000",
            "tolerances":
                {
                    "max": 0.0, 
                    "ave": 0.0
                }
           },
           {
            "run1": "heat1d_1",
            "run2": "heat1d_4",
            "timestamp1": "0.10000000",
            "timestamp2": "0.10000000",
            "tolerances":
                {
                    "max": 0.0, 
                    "ave": 0.0
                }
           },
           {
            "run1": "heat1d_2",
            "run2": "heat1d_4",
            "timestamp1": "0.10000000",
            "timestamp2": "0.10000000",
            "tolerances":
                {
                    "max": 0.0, 
                    "ave": 0.0
                }
           },
           {
            "run1": "heat1d_2",
            "run2": "heat1d_2-full",
            "timestamp1": "0.10000000",
            "timestamp2": "0.10000000",
            "tolerances":
                {
                    "max": 0.0, 
                    "ave": 0.0
                }
           },
           {
            "run1": "heat1d_1",
            "run2": "reference-heat1d_1",
            "timestamp1": "0.10000000",
            "timestamp2": "0.10000000",
            "tolerances":
                {
                    "max": 0.0, 
                    "ave": 0.0
                }
           },
           {
            "run1": "heat1d_2",
            "run2": "reference-heat1d_2",
            "timestamp1": "0.10000000",
            "timestamp2": "0.10000000",
            "tolerances":
                {
                    "max": 0.0, 
                    "ave": 0.0
                }
           },
           {
            "run1": "heat1d_4",
            "run2": "reference-heat1d_4",
            "timestamp1": "0.10000000",
            "timestamp2": "0.10000000",
            "tolerances":
                {
                    "max": 0.0, 
                    "ave": 0.0
                }
           }
       ]
}