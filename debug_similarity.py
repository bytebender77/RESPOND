
from src.embeddings.text_embedder import TextEmbedder
import math

def compute_similarity(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    return dot_product / (norm1 * norm2)

embedder = TextEmbedder()

text1 = "Aftershock felt in zone-1, people panicking and buildings shaking"
text2 = "Seismic sensor detected aftershock activity in zone-1, warning issued"

vec1 = embedder.embed_text(text1)
vec2 = embedder.embed_text(text2)

score = compute_similarity(vec1, vec2)
print(f"Similarity Score: {score}")
