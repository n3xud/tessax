import psycopg
from pgvector.psycopg import register_vector

from contextlib import contextmanager

from .node import Node
db_info = {
"dbname": "example_db",
"user": "postgres",
"password": "password",
"host": "localhost",
"port": 5432,
"autocommit": True,
}

@contextmanager
def get_db():   
    conn = psycopg.connect(**db_info)
    register_vector(conn)
    cur = conn.cursor()
    try:
        yield cur
    finally:
        conn.close()

def insert_data(cur,root_node:Node,parent_id=None):
    
    cur.execute("""INSERT INTO html_nodes (parent_id,content,embedding) 
                VALUES (%s,%s,%s)
                RETURNING id             
                """,(
                    parent_id," ".join(root_node.content) if root_node.content else None,
                    root_node.vector if root_node.vector is not None else None

                    
                ))
    node_id = cur.fetchone()[0]
    print(node_id)
    print(root_node.content)
    print("---------------------------------------")
    for children in root_node.children:
        insert_data(cur,children,node_id)
            


        
def create_index():
    with get_db() as cur:
        cur.execute("""
                   
        CREATE INDEX ON html_nodes
            USING GIN (to_tsvector('english', content));
        CREATE INDEX ON html_nodes
            USING hnsw(embedding vector_cosine_ops) WITH (ef_construction=256);
                    
            """)
        
def search(embedding):
    with get_db() as cur:
        cur.execute("""
            SELECT id,parent_id, content, rank() OVER (ORDER BY %s <=> embedding) AS rank
            FROM html_nodes
            ORDER BY %s <=> embedding
            LIMIT 10        
                    
            """,(embedding,embedding))
        rows = cur.fetchall()
    return rows