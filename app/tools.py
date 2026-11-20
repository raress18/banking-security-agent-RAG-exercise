from typing import Callable
from app.store import store


def build_tools_for_user(user_id: str) -> list[Callable]:
    """Construiește tool-urile izolate strict pe user_id-ul curent."""

    def get_transactions(merchant_query: str | None = None) -> list[dict]:
        """Returnează istoricul tranzacțiilor utilizatorului curent.

        Args:
            merchant_query: Filtru opțional după numele comerciantului (ex: 'GLOVO', 'DRI', 'ATM').
        """
        txs = store.get_transactions_by_user(user_id)
        if merchant_query:
            q = merchant_query.strip().upper()
            txs = [tx for tx in txs if q in tx.merchant_raw.upper()]
        return [tx.model_dump() for tx in txs]


    def check_merchant_reputation(merchant_raw: str) -> dict:  
        """ Verifica reputatia si scorul de risc al unui comerciant dupa numele brut de pe extras.

        Args:
        merchant_raw: Numele exact al comerciantului asa cum apare in tranzactie"""

        merchant = store.get_merchant(merchant_raw)
        if(merchant):
            return merchant.model_dump()
        return {
            "merchant_raw" : merchant_raw,
            "risk_score" : "unknown",
            "notes" : "Comerciantul nu apare in lista noastra." 
        }


    def freeze_card(card_id: str, reason: str) -> dict:
        """Blocheaza temporar un card activ al utilizatorului curent.

        Args:
            card_id: ID-ul cardului (ex: 'card_01'), obtinut din lista tranzactiilor.
            reason: Motivul blocarii cardului."""

        card = store.get_card_by_id(card_id)
        if not card or card.user_id != user_id:
            return { "error" : "Card neautorizat."}
        card.status = "frozen"
        card.freeze_reason = reason
        return { "status" : card.status}


    def create_dispute(transaction_id: str, reason_code: str, confirmed: bool = False) -> dict:
        """Deschide o disputa pentru o tranzactie finalizata a utilizatorului curent.

        Args:
            transaction_id: ID-ul tranzactiei disputate (ex: 'tx_001').
            reason_code: Codul motivului (ex: 'fraud', 'unrecognized_merchant', 'duplicate').
            confirmed: Seteaza True doar dupa ce clientul confirma explicit sumele peste 500 RON.
        """
        txs = store.get_transactions_by_user(user_id)
        tx = None
        for item in txs:
            if item.id == transaction_id:
                tx=item
                break
        if not tx:
            return {"error" : "Tranzactie inexistenta."}
        if tx.status == "pending":
            return {"error": "Tranzactia este pending si nu poate fi disputata."}
        if tx.amount > 500 and not confirmed:
            return {"status": "confirmation_required", "message": "Suma depaseste 500 RON. Cere confirmarea explicita a clientului inainte de a apela din nou cu confirmed=True."}
        dispute = {
            "id": f"disp_{len(store.disputes) + 1:02d}",
            "user_id": user_id,
            "transaction_id": tx.id,
            "amount": tx.amount,
            "reason_code": reason_code,
            "status": "open",
        } 
        store.add_dispute(dispute)
        return {"status": "dispute_created", "dispute": dispute}

    return [get_transactions, check_merchant_reputation, freeze_card, create_dispute]  # adaugă aici și celelalte 3 funcții
