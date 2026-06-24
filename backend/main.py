import os
import json
import sqlite3
import bcrypt
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from datetime import timedelta
from dotenv import load_dotenv

# Import database helpers
from database import get_db, init_db, close_db

# Import AI capabilities
from ai_model import (
    init_faiss, add_to_faiss, get_embedding, 
    classify_topic, find_similar_questions, agent
)

load_dotenv()

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "fallback-secret-for-dev-only")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

CORS(app, resources={r"/api/*": {"origins": "*"}})
jwt = JWTManager(app)
app.teardown_appcontext(close_db)

# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------
@app.route("/api/auth/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    db = get_db()
    try:
        db.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, pw_hash))
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered"}), 409

    user_id = db.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()["id"]
    token = create_access_token(identity=str(user_id))
    return jsonify({"token": token, "email": email}), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    db = get_db()
    row = db.execute("SELECT id, password_hash FROM users WHERE email=?", (email,)).fetchone()
    
    if not row or not bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(row["id"]))
    return jsonify({"token": token, "email": email}), 200


# ---------------------------------------------------------------------------
# Question routes
# ---------------------------------------------------------------------------
@app.route("/api/questions", methods=["POST"])
@jwt_required()
def ask_question():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"error": "Question text required"}), 400
    if len(text) > 1000:
        return jsonify({"error": "Question too long (max 1000 chars)"}), 400

    embedding = get_embedding(text)
    similar = find_similar_questions(embedding)
    topic = classify_topic(text)
    
    # Agentic Generation
    agent_resp = agent.generate_response(text, topic, similar)

    db = get_db()
    cur = db.execute(
        "INSERT INTO questions (user_id, text, topic, embedding, similar_ids, agent_response) VALUES (?,?,?,?,?,?)",
        (user_id, text, topic, embedding.tobytes(), json.dumps([s["id"] for s in similar]), agent_resp)
    )
    db.commit()
    question_id = cur.lastrowid
    
    # Update FAISS Index immediately
    add_to_faiss(question_id, embedding)

    return jsonify({
        "id": question_id,
        "text": text,
        "topic": topic,
        "similar": similar,
        "agent_response": agent_resp,
        "created_at": db.execute("SELECT created_at FROM questions WHERE id=?", (question_id,)).fetchone()["created_at"]
    }), 201


@app.route("/api/questions", methods=["GET"])
@jwt_required()
def get_history():
    user_id = int(get_jwt_identity())
    topic_filter = request.args.get("topic")
    db = get_db()

    # Fixed SQL injection vulnerability by using parameterized query for topic as well
    if topic_filter:
        query = "SELECT id, text, topic, similar_ids, agent_response, created_at FROM questions WHERE user_id=? AND topic=? ORDER BY created_at DESC"
        params = (user_id, topic_filter)
    else:
        query = "SELECT id, text, topic, similar_ids, agent_response, created_at FROM questions WHERE user_id=? ORDER BY created_at DESC"
        params = (user_id,)
        
    rows = db.execute(query, params).fetchall()

    questions = []
    for row in rows:
        sim_ids = json.loads(row["similar_ids"])
        similar = []
        for sid in sim_ids:
            sr = db.execute("SELECT id, text, topic FROM questions WHERE id=?", (sid,)).fetchone()
            if sr:
                similar.append({"id": sr["id"], "text": sr["text"], "topic": sr["topic"]})
                
        questions.append({
            "id": row["id"], 
            "text": row["text"], 
            "topic": row["topic"],
            "similar": similar, 
            "agent_response": row["agent_response"],
            "created_at": row["created_at"],
        })

    return jsonify(questions), 200


@app.route("/api/topics", methods=["GET"])
@jwt_required()
def get_topics():
    user_id = int(get_jwt_identity())
    db = get_db()
    rows = db.execute("SELECT DISTINCT topic FROM questions WHERE user_id=? ORDER BY topic", (user_id,)).fetchall()
    return jsonify([r["topic"] for r in rows]), 200


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    # Initialize FAISS with existing embeddings on server start
    init_faiss()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
