import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from database import get_db

print("Loading sentence-transformer model...")
MODEL = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded.")

# FAISS Index
EMBEDDING_DIM = 384 # all-MiniLM-L6-v2 dimension
index = faiss.IndexFlatIP(EMBEDDING_DIM) # Inner product for cosine similarity if normalized
faiss_id_map = {} # Maps faiss index id to DB id
next_faiss_id = 0

def init_faiss():
    """Load existing embeddings from DB into FAISS."""
    global index, faiss_id_map, next_faiss_id
    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    faiss_id_map = {}
    next_faiss_id = 0
    
    db = get_db()
    rows = db.execute("SELECT id, embedding FROM questions").fetchall()
    
    if not rows:
        return
    
    embeddings = []
    for row in rows:
        emb = np.frombuffer(row["embedding"], dtype=np.float32)
        if emb.shape[0] == EMBEDDING_DIM:
            embeddings.append(emb)
            faiss_id_map[next_faiss_id] = row["id"]
            next_faiss_id += 1
            
    if embeddings:
        matrix = np.vstack(embeddings)
        # Normalize for cosine similarity via Inner Product
        faiss.normalize_L2(matrix)
        index.add(matrix)
    print(f"FAISS index initialized with {index.ntotal} vectors.")

def add_to_faiss(db_id: int, embedding: np.ndarray):
    """Add a new embedding to FAISS."""
    global index, faiss_id_map, next_faiss_id
    # Normalize before adding
    emb_copy = embedding.copy().reshape(1, -1)
    faiss.normalize_L2(emb_copy)
    index.add(emb_copy)
    faiss_id_map[next_faiss_id] = db_id
    next_faiss_id += 1

TOPICS = {
    "Biology": ["cell", "biology", "photosynthesis", "DNA", "genetics", "evolution"],
    "Physics": ["force", "motion", "energy", "gravity", "velocity", "acceleration", "thermodynamics"],
    "Chemistry": ["atom", "molecule", "bond", "reaction", "acid", "base", "element", "compound"],
    "Mathematics": ["algebra", "calculus", "geometry", "trigonometry", "probability", "statistics"],
    "History": ["war", "revolution", "empire", "civilization", "ancient", "medieval", "colonialism"],
    "Literature": ["novel", "poem", "story", "author", "character", "theme", "plot", "Shakespeare"],
    "Computer Science": ["algorithm", "data structure", "programming", "code", "software"],
    "Economics": ["supply", "demand", "market", "price", "inflation", "GDP", "trade"],
    "Geography": ["continent", "country", "capital", "climate", "biome", "population"],
    "General": ["study", "question", "answer", "explanation", "concept"],
}

# Pre-compute topic embeddings
TOPIC_EMBEDDINGS = {
    topic: MODEL.encode(" ".join(phrases))
    for topic, phrases in TOPICS.items()
}

def classify_topic(question: str) -> str:
    q_emb = MODEL.encode(question).reshape(1, -1)
    best_topic, best_score = "General", -1.0
    for topic, t_emb in TOPIC_EMBEDDINGS.items():
        score = np.dot(q_emb[0], t_emb) / (np.linalg.norm(q_emb[0]) * np.linalg.norm(t_emb))
        if score > best_score:
            best_score = score
            best_topic = topic
    return best_topic

def get_embedding(text: str) -> np.ndarray:
    return MODEL.encode(text).astype(np.float32)

def find_similar_questions(embedding: np.ndarray, exclude_user_id: int = None, top_k: int = 5):
    """Return top_k most similar questions using FAISS."""
    if index.ntotal == 0:
        return []
        
    emb_copy = embedding.copy().reshape(1, -1)
    faiss.normalize_L2(emb_copy)
    
    # Search for top_k + 1 in case we need to exclude the perfect match
    D, I = index.search(emb_copy, min(index.ntotal, top_k + 2))
    
    results = []
    db = get_db()
    for i in range(len(I[0])):
        idx = I[0][i]
        score = D[0][i]
        
        if idx == -1:
            continue
            
        db_id = faiss_id_map.get(idx)
        if not db_id:
            continue
            
        if score >= 0.99: # Skip perfect match (likely itself)
            continue
            
        row = db.execute("SELECT id, text, topic FROM questions WHERE id=?", (db_id,)).fetchone()
        if row:
            results.append({
                "id": row["id"], 
                "text": row["text"], 
                "topic": row["topic"], 
                "similarity": round(float(score), 3)
            })
            if len(results) >= top_k:
                break
    return results

class AgenticTutor:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        # In a real system, we'd initialize LangChain or OpenAI client here
        
    def generate_response(self, question: str, topic: str, similar_contexts: list) -> str:
        """
        Agentic Workflow: 
        1. Analyzes the question and topic.
        2. Reviews similar past context (RAG).
        3. Formulates a structured educational answer.
        """
        # If no API key, use a structured fallback heuristic (Mock Agent)
        if not self.api_key:
            return self._mock_generation(question, topic, similar_contexts)
            
        # TODO: Implement real OpenAI/LangChain call here when API key is available.
        return self._mock_generation(question, topic, similar_contexts)
        
    def _mock_generation(self, question: str, topic: str, contexts: list) -> str:
        response = f"### Concept Analysis: {topic}\n\n"
        response += f"Based on our knowledge base, here is a structured breakdown of your question: '{question}'\n\n"
        response += "**Core Principles:**\n"
        response += "- Understanding the fundamental rules of this topic is key.\n"
        response += "- Look for patterns in how variables interact.\n\n"
        
        if contexts:
            response += "**Related Insights:**\n"
            response += "We noticed similar questions were asked before. Exploring those might deepen your understanding:\n"
            for ctx in contexts[:2]:
                response += f"- *{ctx['text']}*\n"
                
        response += "\n**Next Steps:**\n"
        response += "To master this, try solving a practice problem applying this concept or explaining it to someone else!"
        return response

agent = AgenticTutor()
