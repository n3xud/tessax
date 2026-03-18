import psycopg
from pgvector.psycopg import register_vector

db_info = {
    "dbname": "mydatabase",
    "user": "myuser",
    "password": "mypassword",
    "host": "localhost",
    "port": 5432,
    "autocommit": True,
}



# def insert_data(data):
#     with cur.copy("COPY products (content, embedding) FROM STDIN WITH (FORMAT BINARY)") as copy:
#         copy.set_types(["text", "vector"])
#         for content, embedding in (data.sentences, data.embeddings):
#             copy.write_row((content, embedding))

#     cur.close()
#     conn.close()
    
    
def connect_db():
    conn = psycopg.connect(**db_info)
    register_vector(conn)
    cur = conn.cursor()
    return conn , cur
def close_db(conn, cur):
    conn.close()
    cur.close()
    
