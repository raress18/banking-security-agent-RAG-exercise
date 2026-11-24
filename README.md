# Banking Security & Fraud Agent

Asistent AI de securitate bancară construit cu **FastAPI**, **Google GenAI SDK (`gemini-3.8-flash`)** și **RAG**, capabil să analizeze tranzacții suspecte, să blocheze carduri compromise, să deschidă dispute și să aplice politicile interne ale băncii.

## Funcționalități principale

- **Agentic Function Calling:** Orchestrare multi-step în `agent.py` pentru interogarea tranzacțiilor, blocarea cardurilor și inițierea disputelor.
- **Policy Enforcement prin RAG:** Căutare semantică (embeddings + cosine similarity) peste regulamentul bancar (`data/policies.txt`) pentru validarea condițiilor de dispută (ex. tranzacții `pending`, termene de rambursare, plăți recurente).
- **Guardrails & Confirmare Human-in-the-Loop:** Operațiunile cu risc ridicat (ex. dispute peste pragul valoric configurat) necesită confirmare explicită din partea utilizatorului pe același `session_id`.
- **REST API & Containerizare:** Expus prin FastAPI + Uvicorn și pregătit pentru rulare izolată cu Docker Compose.
