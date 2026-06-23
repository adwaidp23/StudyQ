import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from database import get_db

print("Loading sentence-transformer model...")
MODEL = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded.")

TOPICS = {
    "Biology": [
        "cell biology photosynthesis DNA genetics evolution organism species",
        "mitosis meiosis protein enzyme metabolism reproduction heredity",
    ],
    "Physics": [
        "force motion energy gravity velocity acceleration Newton laws thermodynamics",
        "electricity magnetism waves optics quantum mechanics relativity momentum",
    ],
    "Chemistry": [
        "atom molecule bond reaction acid base element compound periodic table",
        "oxidation reduction electrochemistry organic polymer stoichiometry",
    ],
    "Mathematics": [
        "algebra calculus geometry trigonometry probability statistics derivative integral",
        "equation matrix vector polynomial linear function theorem proof",
    ],
    "History": [
        "war revolution empire civilization ancient medieval colonialism independence",
        "democracy government politics society culture historical event timeline",
    ],
    "Literature": [
        "novel poem story author character theme plot metaphor narrative genre",
        "Shakespeare symbolism allegory fiction prose verse literary analysis",
    ],
    "Computer Science": [
        "algorithm data structure programming code software loop recursion array",
        "sorting searching complexity operating system network database binary",
    ],
    "Economics": [
        "supply demand market price inflation GDP trade fiscal monetary policy",
        "microeconomics macroeconomics scarcity opportunity cost elasticity",
        "finance investment portfolio stock analytics banking currency accounting",
    ],
    "Geography": [
        "continent country capital climate biome population urbanization migration",
        "plate tectonics erosion river mountain ecosystem environment",
    ],
    "General": ["study question answer explanation concept definition"],
}

# Pre-compute topic embeddings (one embedding per topic from concatenated phrases)
TOPIC_EMBEDDINGS = {
    topic: MODEL.encode(" ".join(phrases))
    for topic, phrases in TOPICS.items()
}

def classify_topic(question: str) -> str:
    q_emb = MODEL.encode(question).reshape(1, -1)
    best_topic, best_score = "General", -1.0
    for topic, t_emb in TOPIC_EMBEDDINGS.items():
        score = cosine_similarity(q_emb, t_emb.reshape(1, -1))[0][0]
        if score > best_score:
            best_score = score
            best_topic = topic
    return best_topic

def get_embedding(text: str) -> np.ndarray:
    return MODEL.encode(text).astype(np.float32)

def find_similar_questions(embedding: np.ndarray, exclude_user_id: int = None, top_k: int = 5):
    """Return top_k most similar questions from all users (global pool)."""
    db = get_db()
    rows = db.execute(
        "SELECT id, text, topic, embedding, user_id FROM questions"
    ).fetchall()

    if not rows:
        return []

    ids, texts, topics, embeddings = [], [], [], []
    for row in rows:
        emb = np.frombuffer(row["embedding"], dtype=np.float32)
        ids.append(row["id"])
        texts.append(row["text"])
        topics.append(row["topic"])
        embeddings.append(emb)

    matrix = np.vstack(embeddings)
    scores = cosine_similarity(embedding.reshape(1, -1), matrix)[0]

    # Pair and sort, exclude perfect-match (same question just saved)
    ranked = sorted(zip(scores, ids, texts, topics), reverse=True)
    results = []
    for score, qid, text, topic in ranked:
        if score >= 0.99:          # skip itself if already stored
            continue
        results.append({"id": qid, "text": text, "topic": topic, "similarity": round(float(score), 3)})
        if len(results) >= top_k:
            break
    return results
