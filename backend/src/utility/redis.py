from redis import Redis

# redis connection wrapper context manager
class RedisHelper:
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
        self.client = Redis(host=self.host, port=self.port, db=self.db)
    
    def __del__(self):
        self.client.close()

    def __enter__(self):
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
