import redis

# initializing the redis instance
r = redis.Redis(
    host='192.168.0.5',
    port=6379,
    decode_responses=True # <-- this will ensure that binary data is decoded
)

while True:
    message = input("Enter the message you want to send to soilders: ")

    r.publish("army-camp-1", message)
