import boto3

dynamodb = boto3.resource(
    'dynamodb', endpoint_url="http://192.168.0.249:8000",region_name='us-east-1',aws_access_key_id='key',
        aws_secret_access_key= '')

def create_books_table(dynamodb=None,exchange=None):

    
    # Each table/index must have 1 hash key and 0 or 1 range keys.
    
    table = dynamodb.create_table(
        TableName=exchange,
        KeySchema=[

            {
                'AttributeName': 'timestamp_hrs',
                'KeyType': 'HASH'  # Sort key
            },
            {
                'AttributeName': 'timestamp',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'timestamp_hrs',
                # AttributeType refers to the data type 'N' for number type and 'S' stands for string type.
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'timestamp',
                'AttributeType': 'N'
            }
        ],
        ProvisionedThroughput={
            # ReadCapacityUnits set to 10 strongly consistent reads per second
            'ReadCapacityUnits': 1000,
            'WriteCapacityUnits': 1000  # WriteCapacityUnits set to 10 writes per second
        }
    )
    return table

if __name__ == '__main__':
    exchange_list=['bitstamp','bitfinex','itbit','kraken','lmax','cexio','cryptodotcom','bullish','coinbase']
    for exchange_name in exchange_list:
        book_table = create_books_table(dynamodb=dynamodb,exchange=exchange_name)
        print("Status:", book_table.table_status)