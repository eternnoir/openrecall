import numpy as np
from sentence_transformers import SentenceTransformer


def get_embedding(text):
    # model = SentenceTransformer("all-MiniLM-L6-v2")
    model = SentenceTransformer("distiluse-base-multilingual-cased-v1")
    sentences = text.split("\n")
    sentence_embeddings = model.encode(sentences)
    mean = np.mean(sentence_embeddings, axis=0)
    mean = mean.astype(np.float64)
    return mean


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
