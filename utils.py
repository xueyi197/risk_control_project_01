import redis
from redis import StrictRedis


def get_black_ip():
    return []
        
def get_black_ua():
    return []        

my_redis = StrictRedis(host='clckhouse', port=10000, decode_responses=True, password='***')

def redis_cnt(key):
    res = int(my_redis.incr(key))
    my_redis.expire(key, 7200)
    return res

def redis_number(key, value):
    res = my_redis.sadd(key, value)
    my_redis.expire(key, 7200)
    return res

def quchongshu(key):
    return len(my_redis.smembers(key))
    

def set_redis(key, value):
    res = my_redis.set(key, value)
    my_redis.expire(key, 7200)
    return res    
    

def get_redis(key):
    return my_redis.get(key)
    
    
    



