import pandas as pd
import math
import json

df2=pd.read_json('/Users/yeunglaiching/Workspace/iPadCodeApp/Python/Test/graph2/test.json',orient="records")


print(df2)

print(json.dumps(df2.to_json(orient='index')))