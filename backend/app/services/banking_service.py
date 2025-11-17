"""
Banking Service
Handles banking operations including accounts, transactions, and transfers
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from loguru import logger
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from app.models.account import Account, AccountType
from app.models.transaction import Transaction, TransactionStatus, TransactionType
from app.models.user import User


class BankingService:
    """
    Service for banking operations
    Handles accounts, transactions, transfers, and balance inquiries
    """

    def __init__(self, db: Session):
        self.db = db

    async def create_account(
        self,
        user_id: int,
        account_type: AccountType,
        currency: str = "USD",
        initial_balance: Decimal = Decimal("0.00"),
    ) -> Account:
        """
        Create a new bank account for a user

        Args:
            user_id: User ID
            account_type: Type of account (checking, savings, etc.)
            currency: Account currency (default: USD)
            initial_balance: Initial balance (default: 0.00)

        Returns:
            Created Account object

        Raises:
            ValueError: If user not found or invalid parameters
        """
        try:
            # Verify user exists
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User with ID {user_id} not found")

            # Generate unique account number
            account_number = self._generate_account_number(user_id, account_type)

            # Create account
            account = Account(
                user_id=user_id,
                account_number=account_number,
                account_type=account_type,
                balance=initial_balance,
                currency=currency,
                is_active=True,
            )

            self.db.add(account)
            self.db.commit()
            self.db.refresh(account)

            logger.info(
                f"Created {account_type.value} account {account_number} for user {user_id}"
            )

            # If initial balance > 0, create initial deposit transaction
            if initial_balance > 0:
                await self._create_transaction(
                    account_id=account.id,
                    transaction_type=TransactionType.DEPOSIT,
                    amount=initial_balance,
                    description="Initial deposit",
                    status=TransactionStatus.COMPLETED,
                )

            return account

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create account: {str(e)}")
            raise

    def _generate_account_number(self, user_id: int, account_type: AccountType) -> str:
        """
        Generate unique account number

        Args:
            user_id: User ID
            account_type: Account type

        Returns:
            Account number string (format: TTTTYYYYXXXXXXXX)
            TTTT = account type code
            YYYY = user ID (padded)
            XXXXXXXX = sequence number
        """
        # Account type codes
        type_codes = {
            AccountType.CHECKING: "1000",
            AccountType.SAVINGS: "2000",
            AccountType.CREDIT: "3000",
            AccountType.INVESTMENT: "4000",
        }

        type_code = type_codes.get(account_type, "9000")
        user_code = str(user_id).zfill(4)

        # Get count of existing accounts for this user
        count = (
            self.db.query(func.count(Account.id))
            .filter(Account.user_id == user_id)
            .scalar()
        )
        sequence = str(count + 1).zfill(8)

        return f"{type_code}{user_code}{sequence}"

    async def get_account(self, account_id: int) -> Optional[Account]:
        """
        Get account by ID

        Args:
            account_id: Account ID

        Returns:
            Account object or None if not found
        """
        return self.db.query(Account).filter(Account.id == account_id).first()

    async def get_account_by_number(self, account_number: str) -> Optional[Account]:
        """
        Get account by account number

        Args:
            account_number: Account number

        Returns:
            Account object or None if not found
        """
        return (
            self.db.query(Account)
            .filter(Account.account_number == account_number)
            .first()
        )

    async def get_user_accounts(
        self, user_id: int, active_only: bool = True
    ) -> List[Account]:
        """
        Get all accounts for a user

        Args:
            user_id: User ID
            active_only: If True, only return active accounts

        Returns:
            List of Account objects
        """
        query = self.db.query(Account).filter(Account.user_id == user_id)

        if active_only:
            query = query.filter(Account.is_active == True)

        return query.order_by(Account.created_at.desc()).all()

    async def get_balance(self, account_id: int) -> Optional[Decimal]:
        """
        Get current balance of an account

        Args:
            account_id: Account ID

        Returns:
            Account balance or None if account not found
        """
        account = await self.get_account(account_id)
        return account.balance if account else None

    async def deposit(
        self,
        account_id: int,
        amount: Decimal,
        description: Optional[str] = None,
        reference: Optional[str] = None,
    ) -> Transaction:
        """
        Deposit funds into an account

        Args:
            account_id: Account ID
            amount: Amount to deposit (must be positive)
            description: Optional transaction description
            reference: Optional reference number

        Returns:
            Transaction object

        Raises:
            ValueError: If invalid amount or account not found
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        account = await self.get_account(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        if not account.is_active:
            raise ValueError(f"Account {account.account_number} is not active")

        try:
            # Update account balance
            account.balance += amount
            account.updated_at = datetime.utcnow()

            # Create transaction record
            transaction = await self._create_transaction(
                account_id=account_id,
                transaction_type=TransactionType.DEPOSIT,
                amount=amount,
                description=description or "Deposit",
                reference=reference,
                status=TransactionStatus.COMPLETED,
                balance_after=account.balance,
            )

            self.db.commit()

            logger.info(
                f"Deposited {amount} {account.currency} to account {account.account_number}"
            )

            return transaction

        except Exception as e:
            self.db.rollback()
            logger.error(f"Deposit failed: {str(e)}")
            raise

    async def withdraw(
        self,
        account_id: int,
        amount: Decimal,
        description: Optional[str] = None,
        reference: Optional[str] = None,
    ) -> Transaction:
        """
        Withdraw funds from an account

        Args:
            account_id: Account ID
            amount: Amount to withdraw (must be positive)
            description: Optional transaction description
            reference: Optional reference number

        Returns:
            Transaction object

        Raises:
            ValueError: If insufficient funds or invalid parameters
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        account = await self.get_account(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        if not account.is_active:
            raise ValueError(f"Account {account.account_number} is not active")

        if account.balance < amount:
            raise ValueError(
                f"Insufficient funds. Balance: {account.balance}, Requested: {amount}"
            )

        try:
            # Update account balance
            account.balance -= amount
            account.updated_at = datetime.utcnow()

            # Create transaction record
            transaction = await self._create_transaction(
                account_id=account_id,
                transaction_type=TransactionType.WITHDRAWAL,
                amount=amount,
                description=description or "Withdrawal",
                reference=reference,
                status=TransactionStatus.COMPLETED,
                balance_after=account.balance,
            )

            self.db.commit()

            logger.info(
                f"Withdrew {amount} {account.currency} from account {account.account_number}"
            )

            return transaction

        except Exception as e:
            self.db.rollback()
            logger.error(f"Withdrawal failed: {str(e)}")
            raise

    async def transfer(
        self,
        from_account_id: int,
        to_account_id: int,
        amount: Decimal,
        description: Optional[str] = None,
        reference: Optional[str] = None,
    ) -> Dict[str, Transaction]:
        """
        Transfer funds between accounts

        Args:
            from_account_id: Source account ID
            to_account_id: Destination account ID
            amount: Amount to transfer (must be positive)
            description: Optional transaction description
            reference: Optional reference number

        Returns:
            Dict with 'debit' and 'credit' transactions

        Raises:
            ValueError: If invalid parameters or insufficient funds
        """
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")

        if from_account_id == to_account_id:
            raise ValueError("Cannot transfer to the same account")

        # Get both accounts
        from_account = await self.get_account(from_account_id)
        to_account = await self.get_account(to_account_id)

        if not from_account:
            raise ValueError(f"Source account {from_account_id} not found")

        if not to_account:
            raise ValueError(f"Destination account {to_account_id} not found")

        if not from_account.is_active:
            raise ValueError(
                f"Source account {from_account.account_number} is not active"
            )

        if not to_account.is_active:
            raise ValueError(
                f"Destination account {to_account.account_number} is not active"
            )

        # Check currency match
        if from_account.currency != to_account.currency:
            raise ValueError(
                f"Currency mismatch: {from_account.currency} != {to_account.currency}"
            )

        # Check sufficient funds
        if from_account.balance < amount:
            raise ValueError(
                f"Insufficient funds. Balance: {from_account.balance}, Requested: {amount}"
            )

        try:
            # Update balances
            from_account.balance -= amount
            to_account.balance += amount
            from_account.updated_at = datetime.utcnow()
            to_account.updated_at = datetime.utcnow()

            # Create debit transaction (from source account)
            debit_transaction = await self._create_transaction(
                account_id=from_account_id,
                transaction_type=TransactionType.TRANSFER,
                amount=amount,
                description=description or f"Transfer to {to_account.account_number}",
                reference=reference,
                status=TransactionStatus.COMPLETED,
                balance_after=from_account.balance,
                related_account_id=to_account_id,
            )

            # Create credit transaction (to destination account)
            credit_transaction = await self._create_transaction(
                account_id=to_account_id,
                transaction_type=TransactionType.TRANSFER,
                amount=amount,
                description=description
                or f"Transfer from {from_account.account_number}",
                reference=reference,
                status=TransactionStatus.COMPLETED,
                balance_after=to_account.balance,
                related_account_id=from_account_id,
            )

            self.db.commit()

            logger.info(
                f"Transferred {amount} {from_account.currency} from "
                f"{from_account.account_number} to {to_account.account_number}"
            )

            return {
                "debit": debit_transaction,
                "credit": credit_transaction,
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Transfer failed: {str(e)}")
            raise

    async def _create_transaction(
        self,
        account_id: int,
        transaction_type: TransactionType,
        amount: Decimal,
        description: str,
        status: TransactionStatus = TransactionStatus.PENDING,
        reference: Optional[str] = None,
        balance_after: Optional[Decimal] = None,
        related_account_id: Optional[int] = None,
    ) -> Transaction:
        """
        Create a transaction record

        Args:
            account_id: Account ID
            transaction_type: Type of transaction
            amount: Transaction amount
            description: Transaction description
            status: Transaction status
            reference: Optional reference number
            balance_after: Balance after transaction
            related_account_id: Optional related account ID (for transfers)

        Returns:
            Created Transaction object
        """
        transaction = Transaction(
            account_id=account_id,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            status=status,
            reference=reference,
            balance_after=balance_after,
        )

        self.db.add(transaction)
        self.db.flush()  # Flush to get the ID without committing

        return transaction

    async def get_transaction_history(
        self,
        account_id: int,
        limit: int = 50,
        offset: int = 0,
        transaction_type: Optional[TransactionType] = None,
        status: Optional[TransactionStatus] = None,
    ) -> List[Transaction]:
        """
        Get transaction history for an account

        Args:
            account_id: Account ID
            limit: Maximum number of transactions to return
            offset: Offset for pagination
            transaction_type: Optional filter by transaction type
            status: Optional filter by status

        Returns:
            List of Transaction objects
        """
        query = self.db.query(Transaction).filter(Transaction.account_id == account_id)

        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)

        if status:
            query = query.filter(Transaction.status == status)

        transactions = (
            query.order_by(desc(Transaction.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

        return transactions

    async def get_account_summary(self, account_id: int) -> Dict[str, Any]:
        """
        Get comprehensive account summary

        Args:
            account_id: Account ID

        Returns:
            Dict with account details and statistics

        Example:
            {
                "account": {...},
                "balance": 1500.00,
                "total_deposits": 5000.00,
                "total_withdrawals": 3500.00,
                "transaction_count": 42,
                "recent_transactions": [...]
            }
        """
        account = await self.get_account(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        # Get transaction statistics
        deposits = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.account_id == account_id,
                Transaction.transaction_type == TransactionType.DEPOSIT,
                Transaction.status == TransactionStatus.COMPLETED,
            )
        ).scalar() or Decimal("0.00")

        withdrawals = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.account_id == account_id,
                Transaction.transaction_type == TransactionType.WITHDRAWAL,
                Transaction.status == TransactionStatus.COMPLETED,
            )
        ).scalar() or Decimal("0.00")

        transaction_count = (
            self.db.query(func.count(Transaction.id))
            .filter(Transaction.account_id == account_id)
            .scalar()
        )

        # Get recent transactions
        recent_transactions = await self.get_transaction_history(
            account_id=account_id, limit=10
        )

        return {
            "account": account,
            "balance": float(account.balance),
            "currency": account.currency,
            "total_deposits": float(deposits),
            "total_withdrawals": float(withdrawals),
            "transaction_count": transaction_count,
            "recent_transactions": recent_transactions,
        }

    async def close_account(self, account_id: int) -> Account:
        """
        Close/deactivate an account

        Args:
            account_id: Account ID

        Returns:
            Updated Account object

        Raises:
            ValueError: If account has balance or not found
        """
        account = await self.get_account(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        if account.balance != 0:
            raise ValueError(
                f"Cannot close account with non-zero balance: {account.balance}"
            )

        try:
            account.is_active = False
            account.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(account)

            logger.info(f"Closed account {account.account_number}")

            return account

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to close account: {str(e)}")
            raise

    async def reactivate_account(self, account_id: int) -> Account:
        """
        Reactivate a closed account

        Args:
            account_id: Account ID

        Returns:
            Updated Account object
        """
        account = await self.get_account(account_id)
        if not account:
            raise ValueError(f"Account {account_id} not found")

        try:
            account.is_active = True
            account.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(account)

            logger.info(f"Reactivated account {account.account_number}")

            return account

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to reactivate account: {str(e)}")
            raise


def get_banking_service(db: Session) -> BankingService:
    """
    Get BankingService instance

    Args:
        db: Database session

    Returns:
        BankingService instance
    """
    return BankingService(db)
