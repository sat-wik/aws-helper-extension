import json
import cohere
import numpy as np
import faiss
import time
from tqdm import tqdm
import os

# Load scraped data from JSON file
def load_data(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data

# Preprocess the data
def preprocess_data(data):
    documents = []
    for entry in data:
        content = entry.get("content", "").strip()
        if content:
            documents.append({"url": entry["url"], "content": content})
    return documents

# Generate embeddings using Cohere API with rate limiting and retries
def generate_embeddings(documents, cohere_client, batch_size=32, max_tokens_per_minute=100000):
    contents = [doc["content"] for doc in documents]
    embeddings = []

    for i in tqdm(range(0, len(contents), batch_size), desc="Generating embeddings"):
        batch = contents[i:i + batch_size]
        total_tokens = sum(len(content.split()) for content in batch)

        # Rate limit handling
        if total_tokens > max_tokens_per_minute:
            print("Rate limit exceeded. Waiting for 60 seconds...")
            time.sleep(60)

        attempts = 0
        success = False
        while attempts < 3 and not success:
            try:
                response = cohere_client.embed(texts=batch, model="embed-english-light-v2.0")
                embeddings.extend(response.embeddings)
                success = True
            except cohere.errors.TooManyRequestsError as e:
                attempts += 1
                print(f"Rate limit error on attempt {attempts}: {e}")
                if attempts < 3:
                    print("Retrying in 60 seconds...")
                    time.sleep(60)
                else:
                    print("Max retries reached. Skipping this batch.")
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

    return np.array(embeddings, dtype=np.float32)

# Store embeddings in FAISS index
def create_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

# Save the FAISS index
def save_faiss_index(index, file_path):
    faiss.write_index(index, file_path)

# Main function
def main():
    # File paths
    input_file = "scraped_data.json"
    faiss_index_file = "faiss_index.idx"

    # Cohere API key (replace with your actual API key)
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    cohere_client = cohere.Client(COHERE_API_KEY)

    # Load data
    print("Loading data...")
    raw_data = load_data(input_file)

    # Preprocess data
    print("Preprocessing data...")
    documents = preprocess_data(raw_data)

    # Generate embeddings
    print("Generating embeddings...")
    embeddings = generate_embeddings(documents, cohere_client)

    # Create FAISS index
    print("Creating FAISS index...")
    index = create_faiss_index(embeddings)

    # Save FAISS index
    print("Saving FAISS index...")
    save_faiss_index(index, faiss_index_file)

    print("FAISS index saved to", faiss_index_file)

if __name__ == "__main__":
    main()
