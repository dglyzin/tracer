{    
    "runs": [
        {
            "project": "brusselator1d.json",
            "postfix": "half",
            "params": ""
        },
        {
            "project": "brusselator1d.json",
            "postfix": "half", 
            "params": "-cont -finish 0.1"
        },
        {
            "project": "brusselator1d.json",
            "postfix": "full", 
            "params": "-finish 0.1"
        }
        
    ],
    "tests":
        [
            {
            "run1": "brusselator1d-half",
            "run2": "brusselator1d-full",
            "timestamp1": "0.1",
            "timestamp2": "0.1",
            "tolerances":
                {
                    "max": 0.0, 
                    "ave": 0.0
                }
           },
           {
            "run1": "brusselator1d-half",
            "run2": "reference-brusselator1d-half",
            "timestamp1": "0.05",
            "timestamp2": "0.05",
            "tolerances":
                {
                    "max": 0.0, 
                    "ave": 0.0
                }
           },
           {
            "run1": "brusselator1d-full",
            "run2": "reference-brusselator1d-full",
            "timestamp1": "0.1",
            "timestamp2": "0.1",
            "tolerances":
                {
                    "max": 0.0, 
                    "ave": 0.0
                }
           }

           
       ]
}