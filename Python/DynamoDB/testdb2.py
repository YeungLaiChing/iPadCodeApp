from datetime import datetime
from decimal import Decimal
from pathlib import Path

import boto3.session
import pandas as pd
from boto3.dynamodb.conditions import Attr, Key

import awswrangler as wr
import boto3 as boto3


table_name = "movies"
dynamodb = boto3.client('dynamodb',endpoint_url='http://192.168.0.9:8000',region_name='us-west-2',aws_access_key_id='DUMMYIDEXAMPLE',
         aws_secret_access_key= 'DUMMYEXAMPLEKEY')

session=boto3.Session()
df = pd.DataFrame(
    {
        "title": ["Titanic", "Snatch", "The Godfather"],
        "year": [1997, 2000, 1972],
        "genre": ["drama", "caper story", "crime"],
    }
)

wr.dynamodb.put_df(df=df, table_name=table_name,boto3_session=dynamodb)

wr.dynamodb.read_partiql_query(
    query=f"SELECT * FROM {table_name} WHERE title=? AND year=?",
    parameters=["Snatch", 2000],
)