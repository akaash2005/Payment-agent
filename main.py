from flask import Flask, request, jsonify, Response
from groq import Groq
from prompt import SYSTEM_PROMPT
from parse_customers import load_customers
from dotenv import load_dotenv
import json
import os

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load all customers at startup
customers = load_customers()
customer_map = {c["phone_number"].replace(" ", ""): c for c in customers}

def get_customer(phone_number=None):
    if phone_number:
        clean = phone_number.replace(" ", "")
        if clean in customer_map:
            return customer_map[clean]
    # Default to first customer if no match
    return customers[0] if customers else None

@app.route("/voice/chat/completions", methods=["POST"])
def voice():
    data = request.json
    print("Incoming payload:", data)

    messages = data.get("messages", [])
    conversation = [m for m in messages if m["role"] != "system"]

    # Try to get phone number from Vapi payload
    phone_number = None
    call = data.get("call", {})
    if call:
        phone_number = call.get("customer", {}).get("number")

    customer = get_customer(phone_number)

    if not customer:
        return jsonify({"error": "No customer found"}), 400

    system = SYSTEM_PROMPT.format(
        customer_name=customer["customer_name"],
        amount=customer["amount_spoken"],
        due_date=customer["due_date_spoken"],
        attempts=customer["attempts"],
        payment_plan_eligible=customer["payment_plan_eligible"],
        notes=customer["notes"]
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

