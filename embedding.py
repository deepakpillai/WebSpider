from sentence_transformers import SentenceTransformer

def get_embedding(data_to_embed):
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = model.encode(data_to_embed)
    return embeddings