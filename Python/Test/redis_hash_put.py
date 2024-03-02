import redis
import time

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)

r.hset("0005.HK", "price", "60.5")
r.hset("0005.HK", "turnover", "3746838")
print(r.hkeys("0005.HK")) 
print(r.hget("0005.HK", "price"))    
print(r.hmget("0005.HK", "price", "turnover"))
r.hsetnx("0005.HK", "price", "70")
print(r.hget("0005.HK", "price"))
r.hset("0005.HK", "price","71")
print(r.hget("0005.HK","price")
