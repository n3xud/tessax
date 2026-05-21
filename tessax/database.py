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

def insert_data(root_node:Node,parent_id=None):
    
    with get_db() as cur:
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
            insert_data(children,node_id)
            


        
def create_index():
    with get_db() as cur:
        cur.execute("""
                 
        CREATE INDEX ON html_nodes
            USING GIN (to_tsvector('simple', content));
        CREATE INDEX ON html_nodes
            USING hnsw(embedding vector_cosine_ops) WITH (ef_construction=256);
        
                    
            """)
        
def search(text,embedding):
    with get_db() as cur:
        cur.execute("""
            SELECT
                searches.id,
                searches.content,
                searches.parent_id,
                sum(rrf_score(searches.rank)) AS score          
            FROM (
                (
                        SELECT id, content,parent_id, rank() OVER (ORDER BY %s <=> embedding) AS rank
                        FROM html_nodes
                        ORDER BY %s <=> embedding
                        LIMIT 10    
                        )    
                        UNION ALL
                        (
                        SELECT
                            id,
                            content,
                            parent_id,
                            rank() OVER (ORDER BY ts_rank_cd(to_tsvector(content), plainto_tsquery(%s)) DESC) AS rank
                        FROM html_nodes
                        WHERE
                            plainto_tsquery('simple', %s) @@ to_tsvector('simple', content)
                        ORDER BY rank
                        LIMIT 40
                        )
            ) searches
            GROUP BY searches.id ,searches.content, searches.parent_id
            ORDER BY score DESC
            LIMIT 5;
                    
            """,(embedding,embedding,text,text))
        rows = cur.fetchall()
    return rows




def get_parent(id:int):
    with get_db() as cur:
        cur.execute("""
                    SELECT
                        id,
                        content
                    FROM html_nodes
                    WHERE id = %s
                    LIMIT 1;

                    """,(id,))
        row = cur.fetchone()
    return row


def get_siblings(id:int):
    with get_db() as cur:
        cur.execute("""
                    SELECT
                    id,content
                    FROM html_nodes
                    WHERE parent_id = %s
                    
                    
                    
                    """,(id,))
        rows = cur.fetchall()
    return rows


def delete_entries():
    table_name ="html_nodes"
    with get_db() as cur:
        cur.execute("""
                    TRUNCATE TABLE html_nodes RESTART IDENTITY;
                    """)