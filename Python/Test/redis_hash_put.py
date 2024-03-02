import redis
import time

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)

r.hset("0005.HK", "price", "60.5")
r.hset("0005.HK", "turnover", "3746838")
print(r.hkeys("0005.HK")) # 取hash中所有的key
print(r.hget("0005.HK", "price"))    # 单个取hash的key对应的值
print(r.hmget("0005.HK", "price", "turnover")) # 多个取hash的key对应的值
r.hsetnx("0005.HK", "price", "70") # 只能新建
print(r.hget("0005.HK", "price"))
r.hset("0005.HK", "price","71")
print(r.hget("0005.HK","price")
