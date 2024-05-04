import boto3
def create():
    session1 = boto3.Session(
    aws_access_key_id='test1',
    aws_secret_access_key='test1',
    region='us-east-1'
    )
    
    
    session2 = boto3.Session(
    aws_access_key_id='test2',
    aws_secret_access_key='test2',
    region='us-east-1'
    )
    create_books_table(session1)
    create_books_table(session2)
    
def create_books_table(session):
    dynamodb=session.resource('dynamodb',endpoint_url="http://192.168.0.3:8000")
    table = dynamodb.create_table(
        TableName='Books',
        KeySchema=[
            {
                'AttributeName': 'book_id',
                'KeyType': 'HASH'  # Partition key
            }
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
    print(f"table status is {table.table_status}")

if __name__ == '__main__':
    create()