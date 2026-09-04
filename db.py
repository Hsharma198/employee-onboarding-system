import psycopg2
import os



# # for deployment 


# def get_connection():
#     connection = psycopg2.connect(
#         os.getenv("DATABASE_URL")
#     )

#     return connection




def get_connection():
    connection = psycopg2.connect(
        database="hrms_db",
        user="postgres",
        password="admin123",
        host="localhost",
        #host="postgres-container",
        port="5432"
    )

    return connection