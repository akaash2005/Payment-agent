from flask import Flask, request, jsonify, Response
from groq import Groq
from prompt import SYSTEM_PROMPT
from dotenv import load_dotenv
import json
import os

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route("/voice/chat/completions", methods=["POST"])
def voice():
    data = request.json
    print("Incoming payload:", data)

    messages = data.get("messages", [])

    conversation = [m for m in messages if m["role"] != "system"]

    system = SYSTEM_PROMPT.format(
        customer_name="Rahul Mehta",
        amount="Rs. 12,500",
        due_date="March 1, 2026",
        attempts="3"
    )

    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=300,
        messages=[{"role": "system", "content": system}] + conversation,
        stream=True
    )

    def generate():
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield f"data: {json.dumps({'choices': [{'delta': {'role': 'assistant', 'content': delta}}]})}\n\n"
        yield "data: [DONE]\n\n"

    return Response(generate(), mimetype="text/event-stream")

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"})

if __name__ == "__main__":
    app.run(port=5000, debug=True)