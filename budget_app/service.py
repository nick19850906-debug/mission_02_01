import uuid
import csv
import os
from datetime import datetime
from collections import defaultdict
from typing import List, Optional
from .repository import Repository
from .models import Transaction, Category
from .utils import BudgetAppError, handle_errors

class BudgetService:
    """비즈니스 로직과 데이터 검증을 담당하는 계층 (서비스)"""
    def __init__(self, data_dir: str = "./data"):
        self.repo = Repository(data_dir)

    def _validate_date(self, date_str: str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise BudgetAppError("날짜 형식이 올바르지 않습니다 (YYYY-MM-DD).", hint="예: 2024-01-15")

    def _validate_type(self, t: str):
        if t not in ("income", "expense"):
            raise BudgetAppError("타입이 올바르지 않습니다.", hint="income 또는 expense 중 하나를 입력하세요.")

    def _validate_amount(self, amt: int):
        if amt <= 0:
            raise BudgetAppError("금액은 양수여야 합니다.", hint="0보다 큰 값을 입력하세요.")

    def _validate_category(self, cat: str):
        cats = [c.name for c in self.repo.get_categories()]
        if cat not in cats:
            raise BudgetAppError(f"'{cat}' 카테고리가 존재하지 않습니다.", hint=f"등록된 카테고리: {', '.join(cats)}")

    @handle_errors
    def add_transaction_interactive(self):
        date = input("날짜(YYYY-MM-DD): ")
        self._validate_date(date)
        
        t_type = input("타입(income/expense): ")
        self._validate_type(t_type)
        
        cat = input("카테고리: ")
        self._validate_category(cat)
        
        try:
            amount = int(input("금액(양수): "))
            self._validate_amount(amount)
        except ValueError:
            raise BudgetAppError("금액은 숫자여야 합니다.")
            
        memo = input("메모(선택): ")
        tags = input("태그(쉼표로 구분, 없으면 엔터): ")
        
        tx_id = f"TX-{uuid.uuid4().hex[:6].upper()}"
        tx = Transaction(tx_id, t_type, date, amount, cat, memo, tags)
        
        self.repo.save_transaction(tx)
        print(f"[저장 완료] id={tx.id}")

    @handle_errors
    def list_transactions(self, limit: int = None):
        txs = list(self.repo.get_transactions())
        txs.sort(key=lambda x: x.date, reverse=True)
        if limit:
            txs = txs[:limit]
            
        for t in txs:
            print(f"{t.id} | {t.date} | {t.type} | {t.category} | {t.amount} | {t.memo}")

    @handle_errors
    def search_transactions(self, from_date, to_date, category, t_type, q, tag):
        txs = list(self.repo.get_transactions())
        txs.sort(key=lambda x: x.date, reverse=True)
        
        for t in txs:
            if from_date and t.date < from_date: continue
            if to_date and t.date > to_date: continue
            if category and t.category != category: continue
            if t_type and t.type != t_type: continue
            if q and q.lower() not in t.memo.lower(): continue
            if tag and tag.lower() not in t.tags.lower(): continue
            
            print(f"{t.id} | {t.date} | {t.type} | {t.category} | {t.amount} | {t.memo}")

    @handle_errors
    def summary(self, month: str, top: int = 3):
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            raise BudgetAppError("월 형식이 올바르지 않습니다 (YYYY-MM).", hint="예: 2024-01")

        txs = self.repo.get_transactions()
        income = 0
        expense = 0
        cat_expense = defaultdict(int)
        
        has_data = False
        for t in txs:
            if t.date.startswith(month):
                has_data = True
                if t.type == "income":
                    income += t.amount
                else:
                    expense += t.amount
                    cat_expense[t.category] += t.amount
                    
        if not has_data:
            print("데이터 없음")
            return
            
        print(f"총 수입: {income}원")
        print(f"총 지출: {expense}원")
        print(f"잔액: {income - expense}원")
        
        budgets = self.repo.get_budgets()
        if month in budgets:
            budget_amt = budgets[month]
            usage = (expense / budget_amt) * 100 if budget_amt > 0 else 0
            warning = " (경고: 예산 초과!)" if usage > 100 else ""
            print(f"예산: {budget_amt}원 (사용률 {usage:.1f}%){warning}")
            
        print(f"\n지출 TOP {top}")
        sorted_cats = sorted(cat_expense.items(), key=lambda x: x[1], reverse=True)[:top]
        for i, (cat, amt) in enumerate(sorted_cats, 1):
            print(f"{i}) {cat} {amt}원")

    @handle_errors
    def budget_set(self, month: str, amount: int):
        self._validate_amount(amount)
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            raise BudgetAppError("월 형식이 올바르지 않습니다 (YYYY-MM).")
            
        self.repo.set_budget(month, amount)
        print(f"[저장 완료] {month} 예산 {amount}원")

    @handle_errors
    def category_add(self, name: str):
        if not name: raise BudgetAppError("카테고리 이름을 입력하세요.")
        cats = [c.name for c in self.repo.get_categories()]
        if name in cats:
            raise BudgetAppError("이미 존재하는 카테고리입니다.")
        self.repo.add_category(name)
        print(f"[저장 완료] category={name}")
        
    @handle_errors
    def category_list(self):
        for c in self.repo.get_categories():
            print(f"- {c.name}")

    @handle_errors
    def category_remove(self, name: str):
        txs = list(self.repo.get_transactions())
        if any(t.category == name for t in txs):
            raise BudgetAppError("해당 카테고리를 사용하는 내역이 존재하여 삭제할 수 없습니다.")
        self.repo.remove_category(name)
        print(f"[삭제 완료] category={name}")

    @handle_errors
    def delete_transaction(self, tx_id: str):
        txs = list(self.repo.get_transactions())
        new_txs = [t for t in txs if t.id != tx_id]
        
        if len(txs) == len(new_txs):
            print("없는 데이터")
            return
            
        self.repo.overwrite_transactions(iter(new_txs))
        print("[삭제 완료]")

    @handle_errors
    def update_transaction(self, tx_id: str, date, t_type, category, amount, memo, tags):
        txs = list(self.repo.get_transactions())
        found = False
        for t in txs:
            if t.id == tx_id:
                found = True
                if date:
                    self._validate_date(date)
                    t.date = date
                if t_type:
                    self._validate_type(t_type)
                    t.type = t_type
                if category:
                    self._validate_category(category)
                    t.category = category
                if amount:
                    self._validate_amount(amount)
                    t.amount = amount
                if memo is not None: t.memo = memo
                if tags is not None: t.tags = tags
                break
                
        if not found:
            print("없는 데이터")
            return
            
        self.repo.overwrite_transactions(iter(txs))
        print("[수정 완료]")

    @handle_errors
    def export_csv(self, out_path: str, month: str = None, from_date: str = None, to_date: str = None):
        if not month and not (from_date and to_date):
            raise BudgetAppError("내보내기 조건(--month 또는 --from/--to)이 필요합니다.")
            
        txs = list(self.repo.get_transactions())
        count = 0
        with open(out_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["date", "type", "category", "amount", "memo", "tags"])
            for t in txs:
                if month and not t.date.startswith(month): continue
                if from_date and t.date < from_date: continue
                if to_date and t.date > to_date: continue
                
                writer.writerow([t.date, t.type, t.category, t.amount, t.memo, t.tags])
                count += 1
                
        print(f"[완료] {out_path} ({count} records)")

    @handle_errors
    def import_csv(self, in_path: str):
        if not os.path.exists(in_path):
            raise BudgetAppError(f"'{in_path}' 파일이 존재하지 않습니다.")
            
        imported = 0
        skipped = 0
        with open(in_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    self._validate_date(row["date"])
                    self._validate_type(row["type"])
                    self._validate_amount(int(row["amount"]))
                    self._validate_category(row["category"])
                    
                    tx_id = f"TX-{uuid.uuid4().hex[:6].upper()}"
                    tx = Transaction(tx_id, row["type"], row["date"], int(row["amount"]), row["category"], row.get("memo", ""), row.get("tags", ""))
                    self.repo.save_transaction(tx)
                    imported += 1
                except Exception:
                    skipped += 1
                    
        print(f"[완료] imported={imported}, skipped={skipped}")
