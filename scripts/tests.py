#!
import pandas as pd

l = [{
    "date": "2025-11-11",
    "ndvi": "1"
    }, 
    {
    "date": "2025-11-12",
    "ndvi": "2"
    },
    {
    "date": "2025-11-13",
    "ndvi": "3"
    }, 
]

l2 = [{
    "date": "2025-11-11",
    "ndvi": "1"
    } 
]

df = pd.DataFrame(l2)
df["date"] = pd.to_datetime(df["date"])
df.set_index("date", inplace=True)

for index, row in df.itertuples():
    print(index, row)