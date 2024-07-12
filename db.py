import json
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, CollectionDescription, PointStruct
from embedding import get_embedding
import numpy as np
import time

# Initialize Qdrant client
# Install Qdrant client - Follow the below code
# docker pull qdrant/qdrant
# docker run -p 6333:6333 qdrant/qdrant

qdrant_client = QdrantClient("http://localhost:6333")
collection_name = "sc_data"

def do_db(data):
    # Example usage
    insert_to_collection(data)
    
def do_db_ensure(data):
    # Example usage
    if collection_exists():
        print(f"Collection '{collection_name}' already exists.")
        insert_to_collection(data)
    else:
        print(f"Collection '{collection_name}' does not exist.")
        create_collection()
        insert_to_collection(data)
    

# Function to check if collection exists
def collection_exists():
    collections = qdrant_client.get_collections()
    
    for collection in collections:
        for item in collection[1]:
            item:CollectionDescription = item
            if item.name == collection_name:
                return True
    return False

def create_collection():
    # Define collection parameters
    vector_size = 384
    distance_type = Distance.COSINE

    # Create collection
    qdrant_client.create_collection(collection_name=collection_name, vectors_config=VectorParams(size=vector_size, distance=distance_type))
    print("Collection created successfully!")

def delete_collection():
    qdrant_client.delete_collection(collection_name=collection_name)
    
def insert_to_collection(data):
    # Insert data into the collection
    embedding_str = data['title']+data['url']+data['description']
    embedding_vector = get_embedding(embedding_str)
    qdrant_client.upsert(
        collection_name=collection_name,
        points=[
            PointStruct(
                id=int(time.time()),
                payload=data,
                vector=embedding_vector,
            ),
        ],
    )
    print(f"Data inserted successfully! {data['url']}")

def search(query_vector):    
    hits = qdrant_client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=5  # Return 5 closest points
    )
    return hits

def to_file(data):
    with open("results.json", "a") as f:
        json.dump(data, f)
        f.write("\n")

# delete_collection()
# get_all_records()
# create_collection()