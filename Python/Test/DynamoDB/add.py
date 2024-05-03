import boto3

def add_book(books, dynamodb=None):
    dynamodb = boto3.resource( 'dynamodb', endpoint_url="http://192.168.0.3:8000",region_name='us-east-1',aws_access_key_id='key',
         aws_secret_access_key= '')

    books_table = dynamodb.Table('Books')
    response = books_table.put_item(
        Item={
        "book_id": 1005,
        "title": "There Was a Country",
        "author": "Chinua Achebe",
        "isbn": "0143124030",
        "year_of_publication": "2012"

        }
    )


    return response

if __name__ == '__main__':
    book_resp = add_book(books='Books')
    print(book_resp)