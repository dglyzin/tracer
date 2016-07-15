{    
    "runs": [
        {
            "project": "heat_2_2200.json",
            "postfix": "half",
            "params": ""
        },
        {
            "project": "heat_2_2200.json",
            "postfix": "half", 
            "params": "-cont -finish 0.002"
        },
        {
            "project": "heat_2_2200.json",
            "postfix": "full", 
            "params": "-finish 0.002"
        }
        
    ],
    "tests":
        [
           {
            "run1": "heat_2_2200-half",
            "run2": "heat_2_2200-full",
            "timestamp1": "0.00200005",
            "timestamp2": "0.00200005",
            "tolerances":
                {
                    "max": 0.0, 
                    "ave": 0.0
                }
           },
           {
            "run1": "heat_2_2200-half",
            "run2": "reference-heat_2_2200-half",
            "timestamp1": "0.00100000",
            "timestamp2": "0.00100000",
            "tolerances":
                {
                    "max": 0.0, 
                    "ave": 0.0
                }
           },
           {
            "run1": "heat_2_2200-full",
            "run2": "reference-heat_2_2200-full",
            "timestamp1": "0.00200005",
            "timestamp2": "0.00200005",
            "tolerances":
                {
                    "max": 0.0, 
                    "ave": 0.0
                }
           }

       ]
}