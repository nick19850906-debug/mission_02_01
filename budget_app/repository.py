import json
import os
import tempfile
import shutil
from typing import Iterator, List
from .models import Transaction, Category, Budget
from .utils import BudgetAppError

class Repository:
    """파일 I/O를 담당하는 계층 (저장소)"""
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.tx_file = os.path.join(data_dir, "transactions.jsonl")
        self.cat_file = os.path.join(data_dir, "categories.jsonl")
        self.budget_file = os.path.join(data_dir, "budgets.jsonl")
        self._init_files()

    def _init_files(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print("[안내] 데이터 폴더가 생성되었습니다.")
        
        for file_path in [self.tx_file, self.budget_file]:
            if not os.path.exists(file_path):
                open(file_path, 'a').close()
        
        if not os.path.exists(self.cat_file) or os.path.getsize(self.cat_file) == 0:
            print("[안내] 기본 카테고리를 자동 생성합니다.")
            default_cats = ["food", "transport", "rent", "salary", "etc"]
            with open(self.cat_file, 'w', encoding='utf-8') as f:
                for cat in default_cats:
                    f.write(json.dumps({"name": cat}) + "\n")

    # --- 제너레이터 기반 거래 내역 스트리밍 ---
    def get_transactions(self) -> Iterator[Transaction]:
        """yield를 사용하여 대용량 파일도 메모리 부담 없이 읽어옵니다."""
        if not os.path.exists(self.tx_file):
            return
        with open(self.tx_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    yield Transaction.from_dict(json.loads(line))

    def save_transaction(self, tx: Transaction):
        with open(self.tx_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(tx.to_dict(), ensure_ascii=False) + "\n")

    def overwrite_transactions(self, transactions: Iterator[Transaction]):
        """원자성(Atomicity)을 보장하는 덮어쓰기 (임시 파일 후 이름 변경)"""
        fd, temp_path = tempfile.mkstemp(dir=self.data_dir, text=True)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            for tx in transactions:
                f.write(json.dumps(tx.to_dict(), ensure_ascii=False) + "\n")
        shutil.move(temp_path, self.tx_file)

    # --- 카테고리 ---
    def get_categories(self) -> List[Category]:
        cats = []
        with open(self.cat_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    cats.append(Category(**json.loads(line)))
        return cats
        
    def add_category(self, name: str):
        with open(self.cat_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"name": name}, ensure_ascii=False) + "\n")
            
    def remove_category(self, name: str):
        cats = [c for c in self.get_categories() if c.name != name]
        with open(self.cat_file, 'w', encoding='utf-8') as f:
            for c in cats:
                f.write(json.dumps({"name": c.name}, ensure_ascii=False) + "\n")

    # --- 예산 ---
    def set_budget(self, month: str, amount: int):
        budgets = self.get_budgets()
        budgets[month] = amount
        with open(self.budget_file, 'w', encoding='utf-8') as f:
            for m, a in budgets.items():
                f.write(json.dumps({"month": m, "amount": a}, ensure_ascii=False) + "\n")
                
    def get_budgets(self) -> dict:
        budgets = {}
        if not os.path.exists(self.budget_file):
            return budgets
        with open(self.budget_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    budgets[data["month"]] = data["amount"]
        return budgets
