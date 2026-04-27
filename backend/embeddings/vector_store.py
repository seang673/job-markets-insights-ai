from chromadb import Client
from chromadb.config import Settings

#Initialize the ChromaDB client (persistent storage using DuckDB + Parquet)
client = Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="vector_store"))

#Create or load collection
collection = client.get_or_create_collection(name="jobs", metadata={"hnsw:space": "cosine"})

def upsert_job_embedding(job_id: str, embedding:list[float], metadata: dict):
    """
    Insert or update a job embedding in the ChromaDB.
    """
    collection.upsert(
        ids=[job_id],
        embeddings=[embedding],
        metadatas=[metadata]
    )

def query_similar_jobs(embedding: list[float], top_k: int = 5):
    """
    Query for top 5 most similar jobs based on their embeddings (cosine similarity).
    """
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k
    )
    return results

