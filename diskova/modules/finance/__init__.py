"""
Finance Module - Budget, Expenses, Forecasting
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import hashlib


@dataclass
class Transaction:
    id: str
    amount: float
    category: str
    description: str
    date: datetime
    type: str  # income, expense


@dataclass
class Budget:
    id: str
    category: str
    limit: float
    spent: float
    period: str  # monthly, weekly


class FinanceModule:
    def __init__(self, memory_manager):
        self.memory = memory_manager

    def add_transaction(
        self,
        user_id: str,
        amount: float,
        category: str,
        description: str = "",
        date: Optional[datetime] = None,
        transaction_type: str = "expense"
    ) -> Transaction:
        tx_id = hashlib.md5(f"{amount}{category}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        transaction = Transaction(
            id=tx_id,
            amount=amount,
            category=category,
            description=description,
            date=date or datetime.now(),
            type=transaction_type
        )
        
        self.memory.store_preference(f"tx_{tx_id}", user_id, {
            "id": transaction.id,
            "amount": transaction.amount,
            "category": transaction.category,
            "description": transaction.description,
            "date": transaction.date.isoformat(),
            "type": transaction.type
        })
        
        return transaction

    def get_transactions(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category: Optional[str] = None
    ) -> List[Dict]:
        transactions = []
        prefs = self.memory.get_user_context(user_id).preferences
        
        for key, value in prefs.items():
            if key.startswith("tx_") and isinstance(value, dict):
                tx = value
                tx_date = datetime.fromisoformat(tx.get("date", ""))
                
                if start_date and tx_date < start_date:
                    continue
                if end_date and tx_date > end_date:
                    continue
                if category and tx.get("category") != category:
                    continue
                
                transactions.append(tx)
        
        return sorted(transactions, key=lambda x: x.get("date", ""), reverse=True)

    def create_budget(
        self,
        user_id: str,
        category: str,
        limit: float,
        period: str = "monthly"
    ) -> Budget:
        budget_id = hashlib.md5(f"{category}{period}".encode()).hexdigest()[:8]
        
        budget = Budget(
            id=budget_id,
            category=category,
            limit=limit,
            spent=0.0,
            period=period
        )
        
        self.memory.store_preference(f"budget_{budget_id}", user_id, {
            "id": budget.id,
            "category": budget.category,
            "limit": budget.limit,
            "spent": budget.spent,
            "period": budget.period
        })
        
        return budget

    def get_budgets(self, user_id: str) -> List[Dict]:
        budgets = []
        prefs = self.memory.get_user_context(user_id).preferences
        
        for key, value in prefs.items():
            if key.startswith("budget_") and isinstance(value, dict):
                budgets.append(value)
        
        return budgets

    def get_spending_summary(self, user_id: str, period: str = "month") -> Dict:
        transactions = self.get_transactions(user_id)
        
        total_income = sum(
            t.get("amount", 0) 
            for t in transactions 
            if t.get("type") == "income"
        )
        
        total_expense = sum(
            t.get("amount", 0) 
            for t in transactions 
            if t.get("type") == "expense"
        )
        
        by_category = {}
        for t in transactions:
            if t.get("type") == "expense":
                cat = t.get("category", "other")
                by_category[cat] = by_category.get(cat, 0) + t.get("amount", 0)
        
        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - total_expense,
            "by_category": by_category,
            "transaction_count": len(transactions)
        }

    def forecast_cashflow(self, user_id: str, days: int = 30) -> Dict:
        transactions = self.get_transactions(user_id)
        
        daily_avg_income = 0
        daily_avg_expense = 0
        
        if transactions:
            income_tx = [t for t in transactions if t.get("type") == "income"]
            expense_tx = [t for t in transactions if t.get("type") == "expense"]
            
            if income_tx:
                daily_avg_income = sum(t.get("amount", 0) for t in income_tx) / len(income_tx) / 30
            if expense_tx:
                daily_avg_expense = sum(t.get("amount", 0) for t in expense_tx) / len(expense_tx) / 30
        
        projected_income = daily_avg_income * days
        projected_expense = daily_avg_expense * days
        
        return {
            "projected_income": round(projected_income, 2),
            "projected_expense": round(projected_expense, 2),
            "projected_balance": round(projected_income - projected_expense, 2),
            "daily_avg_income": round(daily_avg_income, 2),
            "daily_avg_expense": round(daily_avg_expense, 2)
        }

    def get_top_expenses(self, user_id: str, limit: int = 5) -> List[Dict]:
        transactions = [
            t for t in self.get_transactions(user_id)
            if t.get("type") == "expense"
        ]
        
        return sorted(
            transactions,
            key=lambda x: x.get("amount", 0),
            reverse=True
        )[:limit]