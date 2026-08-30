import psycopg2

def get_connection():
    connection = psycopg2.connect(
        database="hrms_db",
        user="postgres",
        password="admin123",
        # host="localhost",
        host="postgres-container",
        port="5432"
    )

    return connection