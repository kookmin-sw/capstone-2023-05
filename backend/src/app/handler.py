import boto3
import json
import psycopg2


def hello(event, context):

    ENDPOINT = "naruhodoo-db.cldpkmn0dcie.ap-northeast-2.rds.amazonaws.com"
    PORT = "5432"
    USER = "root"
    REGION = "ap-northeast-2"
    DBNAME = "postgres"
    PASSWORD = "password"

    try:

        conn = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME,
                                user=USER, password=PASSWORD, sslrootcert="SSLCERTIFICATE")
        cur = conn.cursor()
        cur.execute("""CREATE TABLE room(
                                        id SERIAL PRIMARY KEY,
                                        name text,
                                        topic text                                        
                        )""")
        # cur.execute("INSERT INTO room VALUES (DEFAULT)")

        conn.commit()

        cur.execute("""select * from room""")
        query_results = cur.fetchall()

        cur.close()
        conn.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "Result": str(query_results)
            })
        }
    except Exception as e:
        print(e)
        return {
            "statusCode": 400,
            "body": json.dumps({
                "Error": str(e)
            })
        }
