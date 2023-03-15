import boto3
import json
import psycopg2


def hello(event, context):

    ENDPOINT = "naruhodoo-db.cldpkmn0dcie.ap-northeast-2.rds.amazonaws.com"
    PORT = "5432"
    USER = "root"
    REGION = "ap-northeast-2"
    DBNAME = "naruhodoo-db"

    print("HELLOOOOOOOOOOOOO!!")
    try:
        client = boto3.client('rds')

        token = client.generate_db_auth_token(
            DBHostname=ENDPOINT, Port=PORT, DBUsername=USER, Region=REGION)

        conn = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME,
                                user=USER, password=token, sslrootcert="SSLCERTIFICATE")
        cur = conn.cursor()
        cur.execute("""SELECT now()""")
        query_results = cur.fetchall()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": query_results
            })
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "Error": e
            })
        }
