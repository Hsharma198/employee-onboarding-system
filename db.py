import psycopg2

def get_connection():
    connection = psycopg2.connect(
        database="hrms_db",
        user="postgres",
        password="admin123",
        host="localhost",
        port="5432"
    )

    return connection