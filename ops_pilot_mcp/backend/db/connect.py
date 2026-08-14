import psycopg


db_params={
    "host": "localhost",
    "port": 5432,
    "database": "opspilot",
    "user": "nour",
    "password": "admin"
}

def connect():
    try:
        with psycopg.connect(**db_params) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                db_version = cur.fetchone()
                print(f"Database version: {db_version[0]}")
    except Exception as e:
        print(f"Failed to connect to the database: {e}")

if __name__ == "__main__":
    connect()