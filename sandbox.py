import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from app.tools import build_tools_for_user
from app.store import store

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
tools = build_tools_for_user("user_123")  # pune un user_id care exista in transactions.json

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Arata-mi tranzactiile mele si verifica daca vreun comerciant e suspect.",
    config=types.GenerateContentConfig(
        tools=tools,
        system_instruction="Esti un asistent bancar de securitate. Foloseste tool-urile disponibile.",
    ),
)

print("Raspuns text:", response.text)
print("Dispute in store:", store.disputes)