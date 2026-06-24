import os
import json
import numpy as np
from database import get_db
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------------------------
# Offline TF-IDF Vectorizer
# ---------------------------------------------------------------------------
VECTORIZER = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), max_features=512, sublinear_tf=True)
WORD_VECTORIZER = TfidfVectorizer(analyzer="word", ngram_range=(1, 2), max_features=512, sublinear_tf=True, stop_words="english")

SEED_CORPUS = [
    "photosynthesis chlorophyll light energy glucose oxygen plant cell biology",
    "force mass acceleration Newton law motion velocity momentum physics",
    "atom element molecule compound bond ionic covalent chemistry",
    "algebra equation calculus derivative integral math statistics",
    "war revolution civilization ancient history democracy government",
    "algorithm data structure programming code software computer science ai agent artificial intelligence machine learning model neural network",
    "supply demand market price inflation economy finance",
    "study question answer explanation concept definition"
]

VECTORIZER.fit(SEED_CORPUS)
WORD_VECTORIZER.fit(SEED_CORPUS)

EMBEDDING_DIM = 1024

def get_embedding(text: str) -> np.ndarray:
    char_vec = VECTORIZER.transform([text]).toarray()[0]
    word_vec = WORD_VECTORIZER.transform([text]).toarray()[0]
    combined = np.concatenate([char_vec, word_vec]).astype(np.float32)
    norm = np.linalg.norm(combined)
    if norm > 0:
        combined = combined / norm
    return combined

# ---------------------------------------------------------------------------
# Native NumPy Vector Search (No FAISS dependency)
# ---------------------------------------------------------------------------
def init_faiss():
    # Stub function since we removed FAISS, main.py still calls it on startup
    pass

def add_to_faiss(db_id: int, embedding: np.ndarray):
    # Stub function since we removed FAISS, main.py still calls it
    pass

TOPICS = {
    "Biology": "cell biology photosynthesis DNA genetics evolution",
    "Physics": "force motion energy gravity velocity acceleration thermodynamics",
    "Chemistry": "atom molecule bond reaction acid base element compound",
    "Mathematics": "algebra calculus geometry trigonometry probability statistics",
    "History": "war revolution civilization ancient medieval colonialism",
    "Literature": "novel poem story author character theme plot Shakespeare",
    "Computer Science": "algorithm data structure programming code software ai agent artificial intelligence machine learning model neural network",
    "Economics": "supply demand market price inflation GDP trade",
    "Geography": "continent country capital climate biome population",
    "General": "study question answer explanation concept",
}

TOPIC_EMBEDDINGS = {topic: get_embedding(phrases) for topic, phrases in TOPICS.items()}

def classify_topic(question: str) -> str:
    q_emb = get_embedding(question)
    best_topic, best_score = "General", -1.0
    for topic, t_emb in TOPIC_EMBEDDINGS.items():
        score = np.dot(q_emb, t_emb)
        if score > best_score:
            best_score = score
            best_topic = topic
    return best_topic

def find_similar_questions(embedding: np.ndarray, exclude_user_id: int = None, top_k: int = 5):
    db = get_db()
    rows = db.execute("SELECT id, text, topic, embedding FROM questions").fetchall()
    
    if not rows:
        return []
        
    ids, texts, topics, embeddings = [], [], [], []
    for row in rows:
        emb = np.frombuffer(row["embedding"], dtype=np.float32)
        if emb.shape[0] == EMBEDDING_DIM:
            ids.append(row["id"])
            texts.append(row["text"])
            topics.append(row["topic"])
            embeddings.append(emb)
            
    if not embeddings:
        return []
        
    matrix = np.vstack(embeddings)
    scores = cosine_similarity(embedding.reshape(1, -1), matrix)[0]
    
    ranked = sorted(zip(scores, ids, texts, topics), reverse=True)
    results = []
    
    for score, qid, text, topic in ranked:
        if score >= 0.99: 
            continue
        if score < 0.05:
            continue
            
        results.append({"id": qid, "text": text, "topic": topic, "similarity": round(float(score), 3)})
        if len(results) >= top_k:
            break
            
    return results

# ---------------------------------------------------------------------------
# Agentic Tutor
# ---------------------------------------------------------------------------
import requests

class AgenticTutor:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        
    def generate_response(self, question: str, topic: str, similar_contexts: list) -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return self._mock_generation(question, topic, similar_contexts)
            
        system_prompt = (
            "You are an expert academic AI tutor.\n"
            "First, determine if the user's input is a valid, coherent academic or study-related question. "
            "If it is complete gibberish (e.g. 'asdasd'), heavily inappropriate, or a non-question, reply exactly with: "
            "'**Invalid Question:** Please ask a clear, coherent study or academic question.' and say nothing else.\n\n"
            f"If it is a valid question, provide a structured explanation under the topic '{topic}'. Use markdown formatting."
        )
        
        if similar_contexts:
            system_prompt += "\nRelated past questions in the system:\n"
            for ctx in similar_contexts[:2]:
                system_prompt += f"- {ctx['text']}\n"
                
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 400
                },
                timeout=15
            )
            data = response.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"]
            else:
                return f"Error from OpenAI: {data.get('error', {}).get('message', 'Unknown error')}"
        except Exception as e:
            return f"Error communicating with AI service: {str(e)}"
        
    def _mock_generation(self, question: str, topic: str, contexts: list) -> str:
        response = f"### Concept Analysis: {topic}\n\n"
        response += f"Based on our knowledge base, here is a structured breakdown of your question: '{question}'\n\n"
        response += "**Core Principles:**\n- Understanding the fundamental rules of this topic is key.\n- Look for patterns in how variables interact.\n\n"
        
        if contexts:
            response += "**Related Insights:**\nWe noticed similar questions were asked before:\n"
            for ctx in contexts[:2]:
                response += f"- *{ctx['text']}*\n"
                
        response += "\n**Next Steps:**\nTo master this, try solving a practice problem applying this concept!"
        response += "\n\n*(Note: This is a placeholder. Set OPENAI_API_KEY in your PythonAnywhere .env file to enable real AI responses!)*"
        return response

agent = AgenticTutor()
