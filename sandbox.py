from app.agent import run_agent
from app.schemas import ChatRequest

req = ChatRequest(
    session_id="test_rag_1",
    user_id="user_01",
    message=(
        "Am vazut o tranzactie suspecta la ATM Euronet Cluj. Ce trebuie sa fac, "
        "in cate zile imi recuperez banii si cat costa un card nou?"
    ),
)

res = run_agent(req)
print("Risk:", res.risk_level)
print("Tools:", res.tools_executed)
print("Actions:", res.actions_taken)
print("Reply:\n", res.reply)