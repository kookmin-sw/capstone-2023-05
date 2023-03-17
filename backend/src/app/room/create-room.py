import json
import psycopg2


def create_room(event, context):

    ENDPOINT = "naruhodoo-db.cldpkmn0dcie.ap-northeast-2.rds.amazonaws.com"
    PORT = "5432"
    USER = "root"
    DBNAME = "postgres"
    PASSWORD = "password"

    try:
        conn = psycopg2.connect(host=ENDPOINT, port=PORT, database=DBNAME,
                                user=USER, password=PASSWORD, sslrootcert="SSLCERTIFICATE")
        cur = conn.cursor()

        # Extract Room Name, Topic
        body = json.loads(event['body'])
        room_name = body['name']
        room_topic = body['topic']

        # Run Query
        cur.execute(
            f"""INSERT INTO room(id, name, topic) VALUES(DEFAULT, \'{room_name}\', \'{room_topic}\')""")
        conn.commit()

        # Close the Connection
        cur.close()
        conn.close()

        return {
            "statusCode": 200,
            "body": json.dumps({
                "Result": "Room creation success"
            })
        }
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "Error": str(e)
            })
        }
