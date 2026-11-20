import json
from pathlib import Path
from app.schemas import Card, MerchantInfo, Transaction

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class Store:
    def __init__(self) -> None:
        self.transactions: list[Transaction] = []
        self.cards: dict[str, Card] = {}
        self.merchants: dict[str, MerchantInfo] = {}
        self.disputes: list[dict] = []
        self.sessions: dict[str, list] = {}
        self.reset()

    def reset(self) -> None:
        with open(DATA_DIR / "transactions.json", "r", encoding="utf-8") as f:
            self.transactions = [Transaction(**item) for item in json.load(f)]

        with open(DATA_DIR / "cards.json", "r", encoding="utf-8") as f:
            raw_cards = [Card(**item) for item in json.load(f)]
            self.cards = {card.id: card for card in raw_cards}

        with open(DATA_DIR / "merchants.json", "r", encoding="utf-8") as f:
            raw_merchants = [MerchantInfo(**item) for item in json.load(f)]
            self.merchants = {m.merchant_raw.upper(): m for m in raw_merchants}

        self.disputes = []
        self.sessions = {}

    def get_transactions_by_user(self, user_id: str) -> list[Transaction]:
        return [tx for tx in self.transactions if tx.user_id == user_id]

    def get_cards_by_user(self, user_id: str) -> list[Card]:
        return [card for card in self.cards.values() if card.user_id == user_id]

    def get_card_by_id(self, card_id: str) -> Card | None:
        return self.cards.get(card_id)

    def get_merchant(self, merchant_raw: str) -> MerchantInfo | None:
        return self.merchants.get(merchant_raw.strip().upper())

    def add_dispute(self, dispute: dict) -> None:
        self.disputes.append(dispute)

    def get_session_history(self, session_id: str) -> list:
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        return self.sessions[session_id]


store = Store()