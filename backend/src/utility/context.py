from redis import Redis
import psycopg2


# redis connection wrapper context manager
class RedisContext:
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
        self.client: Redis = Redis(host=self.host, port=self.port, db=self.db)
    
    def __del__(self):
        self.client.close()

    def __enter__(self):
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()


# postgrese psycopg2 connection wrapper context manager
class PostgresContext:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.client = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.client.cursor()
    
    def __del__(self):
        self.client.close()

    def __enter__(self):
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()