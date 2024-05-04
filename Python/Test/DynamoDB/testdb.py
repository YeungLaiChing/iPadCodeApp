import boto3

def create_books_table(dynamodb=None):
    dynamodb = boto3.resource(
        'dynamodb', endpoint_url="http://192.168.0.3:8000",region_name='us-east-1',aws_access_key_id='key',
         aws_secret_access_key= '')
    table = dynamodb.create_table(
        TableName='Books',
        KeySchema=[
            {
                'AttributeName': 'book_id',
                'KeyType': 'HASH'  # Partition key
            
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'book_id',
                # AttributeType refers to the data type 'N' for number type and 'S' stands for string type.
                'AttributeType': 'N'
            }
        ],
        ProvisionedThroughput={
            # ReadCapacityUnits set to 10 strongly consistent reads per second
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10  # WriteCapacityUnits set to 10 writes per second
        }
    )
    print(table.status)

if __name__ == '__main__':
    create_books_table()
    