import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.schemas import ChatRequest, ChatResponse
from app.store import store
from app.tools import build_tools_for_user

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """Esti un agent bancar de securitate si analiza a fraudelor.
Reguli stricte:
1. Foloseste intotdeauna tool-urile pentru a verifica tranzactiile si comerciantii inainte de a raspunde.
2. Nu inventa date, sume sau ID-uri de carduri/tranzactii.
3. Daca o disputa necesita confirmare (sume peste 500 RON), cere acordul explicit al clientului si asteapta raspunsul lui inainte sa apelezi create_dispute cu confirmed=True.
4. Raspunde clar, concis si profesionist in limba romana."""


def run_agent(request: ChatRequest) -> ChatResponse:
    history = store.get_session_history(request.session_id)
    tools_list = build_tools_for_user(request.user_id)
    tools_map = {fn.__name__: fn for fn in tools_list}

    tools_executed: list[str] = []
    actions_taken: list[str] = []
    requires_confirmation = False
    risk_level = "low"

    history.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=request.message)],
        )
    )

    for _ in range(5):
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=history,
            config=types.GenerateContentConfig(
                tools=tools_list,
                system_instruction=SYSTEM_PROMPT,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
            ),
        )

        model_content = response.candidates[0].content
        history.append(model_content)

        if not response.function_calls:
            return ChatResponse(
                reply=response.text or "",
                risk_level=risk_level,
                requires_confirmation=requires_confirmation,
                actions_taken=actions_taken,
                tools_executed=tools_executed,     
            )

        response_parts = []
        RISK_PRIORITY = {"low": 0, "medium": 1, "high": 2}
        for call in response.function_calls:
            fn = tools_map[call.name]
            result = fn(**(call.args or {}))
            tools_executed.append(call.name)

            if isinstance(result,dict):
                score = result.get("risk_score")
                if score in RISK_PRIORITY and RISK_PRIORITY[score] > RISK_PRIORITY[risk_level]:
                    risk_level = score

                if result.get("status") == "frozen":
                    actions_taken.append(f"card_frozen:{result.get('card_id')}")
                    risk_level = "high"
                if result.get("status") == "dispute_created":
                    dispute_id = result.get("dispute", {}).get("id")
                    actions_taken.append(f"dispute_created:{dispute_id}")
                if result.get("status") == "confirmation_required":
                    requires_confirmation = True

            response_parts.append(
                types.Part.from_function_response(
                    name=call.name,
                    response={"result" : result},
                )
            )

        history.append(
            types.Content(
                role="user", 
                parts=response_parts
            )
        )

    return ChatResponse(
        reply="Limita maxima de pasi ai agentului a fost atinsa.",
        risk_level=risk_level,
        requires_confirmation=requires_confirmation,
        actions_taken=actions_taken,
        tools_executed=tools_executed,
    )