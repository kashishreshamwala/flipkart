from flask import Flask, render_template, request
from dotenv import load_dotenv
import os

from flipkart.data_ingestion import data_ingestion
from flipkart.retrieval_generation import generation

from langchain_core.chat_history import InMemoryChatMessageHistory

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
load_dotenv()

# -------------------------------------------------
# Initialize Vector Store (reuse existing data)
# -------------------------------------------------
vstore = data_ingestion("done")

# -------------------------------------------------
# Initialize RAG chain
# -------------------------------------------------
chain = generation(vstore)

# -------------------------------------------------
# Chat memory store
# -------------------------------------------------
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# -------------------------------------------------
# Flask App
# -------------------------------------------------
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chat():
    user_input = request.form.get("msg")

    response = chain.invoke(
        {"input": user_input},
        config={
            "configurable": {"session_id": "user1"}
        }
    )

    # ✅ response is AIMessage
    return response.content

# -------------------------------------------------
# Run server
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
