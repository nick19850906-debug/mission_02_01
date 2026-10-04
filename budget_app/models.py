from dataclasses import dataclass
from typing import Optional

@dataclass
class Transaction:
    id: str
    type: str  # 'income' 또는 'expense'
    date: str  # 'YYYY-MM-DD' 형태
    amount: int
    category: str
    memo: str = ""
    tags: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "date": self.date,
            "amount": self.amount,
            "category": self.category,
            "memo": self.memo,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

@dataclass
class Category:
    name: str

@dataclass
class Budget:
    month: str  # 'YYYY-MM' 형태
    amount: int
