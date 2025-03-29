"""
Module for converting documents into vector embeddings using OpenAI or LlamaIndex.
"""

import chromadb

# setup Chroma in-memory, for easy prototyping. Can add persistence easily!
client = chromadb.Client()
# Create collection. get_collection, get_or_create_collection, delete_collection also available!
collection = client.create_collection("all-my-documents")

def embed_documents(docs, model="gpt-4"):
    collection.add(
        documents=docs
        metadatas=[{"source": "notion"}]*len(docs)
    )
    # TODO: Call embedding API and return vector representations
    pass

def query():
    # Query/search 2 most similar results. You can also .get by id
    results = collection.query(
        query_texts=["This is a query document"],
        n_results=2,
        # where={"metadata_field": "is_equal_to_this"}, # optional filter
        # where_document={"$contains":"search_string"}  # optional filter
    )