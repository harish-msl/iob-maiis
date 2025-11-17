"""
Banking API Router
Handles banking operations including accounts, transactions, and transfers
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.account import Account, AccountType
from app.models.transaction import Transaction, TransactionStatus, TransactionType
from app.models.user import User
from app.services.banking_service import get_banking_service

router = APIRouter(prefix="/banking", tags=["banking"])

# ============================================================================
# Schemas
# ============================================================================


class AccountCreate(BaseModel):
    """Account creation request"""

    account_type: AccountType = Field(..., description="Type of account to create")
    currency: str = Field("USD", description="Account currency")
    initial_balance: Decimal = Field(
        Decimal("0.00"), ge=0, description="Initial deposit amount"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "account_type": "checking",
                    "currency": "USD",
                    "initial_balance": 1000.00,
                }
            ]
        }
    }


class AccountResponse(BaseModel):
    """Account response"""

    id: int
    user_id: int
    account_number: str
    account_type: AccountType
    balance: Decimal
    currency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "user_id": 1,
                    "account_number": "1000000100000001",
                    "account_type": "checking",
                    "balance": 1500.00,
                    "currency": "USD",
                    "is_active": True,
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z",
                }
            ]
        },
    }


class DepositRequest(BaseModel):
    """Deposit request"""

    account_id: int = Field(..., description="Account ID")
    amount: Decimal = Field(..., gt=0, description="Amount to deposit")
    description: Optional[str] = Field(None, description="Transaction description")
    reference: Optional[str] = Field(None, description="Reference number")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "account_id": 1,
                    "amount": 500.00,
                    "description": "Salary deposit",
                    "reference": "SAL-2024-001",
                }
            ]
        }
    }


class WithdrawRequest(BaseModel):
    """Withdrawal request"""

    account_id: int = Field(..., description="Account ID")
    amount: Decimal = Field(..., gt=0, description="Amount to withdraw")
    description: Optional[str] = Field(None, description="Transaction description")
    reference: Optional[str] = Field(None, description="Reference number")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "account_id": 1,
                    "amount": 200.00,
                    "description": "ATM withdrawal",
                    "reference": "ATM-2024-001",
                }
            ]
        }
    }


class TransferRequest(BaseModel):
    """Transfer request"""

    from_account_id: int = Field(..., description="Source account ID")
    to_account_id: int = Field(..., description="Destination account ID")
    amount: Decimal = Field(..., gt=0, description="Amount to transfer")
    description: Optional[str] = Field(None, description="Transfer description")
    reference: Optional[str] = Field(None, description="Reference number")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "from_account_id": 1,
                    "to_account_id": 2,
                    "amount": 300.00,
                    "description": "Transfer to savings",
                    "reference": "TRF-2024-001",
                }
            ]
        }
    }


class TransactionResponse(BaseModel):
    """Transaction response"""

    id: int
    account_id: int
    transaction_type: TransactionType
    amount: Decimal
    description: str
    status: TransactionStatus
    reference: Optional[str]
    balance_after: Optional[Decimal]
    created_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "account_id": 1,
                    "transaction_type": "deposit",
                    "amount": 500.00,
                    "description": "Salary deposit",
                    "status": "completed",
                    "reference": "SAL-2024-001",
                    "balance_after": 1500.00,
                    "created_at": "2024-01-15T10:30:00Z",
                }
            ]
        },
    }


class BalanceResponse(BaseModel):
    """Balance response"""

    account_id: int
    account_number: str
    balance: Decimal
    currency: str
    as_of: datetime

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "account_id": 1,
                    "account_number": "1000000100000001",
                    "balance": 1500.00,
                    "currency": "USD",
                    "as_of": "2024-01-15T10:30:00Z",
                }
            ]
        }
    }


class AccountSummaryResponse(BaseModel):
    """Account summary response"""

    account: AccountResponse
    balance: float
    currency: str
    total_deposits: float
    total_withdrawals: float
    transaction_count: int
    recent_transactions: List[TransactionResponse]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "account": {
                        "id": 1,
                        "user_id": 1,
                        "account_number": "1000000100000001",
                        "account_type": "checking",
                        "balance": 1500.00,
                        "currency": "USD",
                        "is_active": True,
                    },
                    "balance": 1500.00,
                    "currency": "USD",
                    "total_deposits": 5000.00,
                    "total_withdrawals": 3500.00,
                    "transaction_count": 42,
                    "recent_transactions": [],
                }
            ]
        }
    }


class TransferResponse(BaseModel):
    """Transfer response"""

    debit_transaction: TransactionResponse
    credit_transaction: TransactionResponse
    from_account_balance: Decimal
    to_account_balance: Decimal

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "debit_transaction": {
                        "id": 1,
                        "account_id": 1,
                        "transaction_type": "transfer",
                        "amount": 300.00,
                        "description": "Transfer to account 2000000200000001",
                        "status": "completed",
                    },
                    "credit_transaction": {
                        "id": 2,
                        "account_id": 2,
                        "transaction_type": "transfer",
                        "amount": 300.00,
                        "description": "Transfer from account 1000000100000001",
                        "status": "completed",
                    },
                    "from_account_balance": 1200.00,
                    "to_account_balance": 800.00,
                }
            ]
        }
    }


# ============================================================================
# Endpoints
# ============================================================================


@router.post(
    "/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED
)
async def create_account(
    request: AccountCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Account:
    """
    Create a new bank account for the current user

    Args:
        request: Account creation request
        current_user: Authenticated user
        db: Database session

    Returns:
        Created account

    Example:
        ```
        POST /api/banking/accounts
        {
            "account_type": "savings",
            "currency": "USD",
            "initial_balance": 1000.00
        }
        ```
    """
    try:
        logger.info(f"User {current_user.id} creating {request.account_type} account")

        banking_service = get_banking_service(db)

        account = await banking_service.create_account(
            user_id=current_user.id,
            account_type=request.account_type,
            currency=request.currency,
            initial_balance=request.initial_balance,
        )

        logger.info(
            f"Created account {account.account_number} for user {current_user.id}"
        )

        return account

    except Exception as e:
        logger.error(f"Account creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create account: {str(e)}",
        )


@router.get("/accounts", response_model=List[AccountResponse])
async def list_accounts(
    active_only: bool = Query(True, description="Only return active accounts"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[Account]:
    """
    Get all accounts for the current user

    Args:
        active_only: If true, only return active accounts
        current_user: Authenticated user
        db: Database session

    Returns:
        List of user's accounts
    """
    try:
        logger.info(f"Fetching accounts for user {current_user.id}")

        banking_service = get_banking_service(db)
        accounts = await banking_service.get_user_accounts(
            user_id=current_user.id, active_only=active_only
        )

        return accounts

    except Exception as e:
        logger.error(f"Failed to fetch accounts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch accounts",
        )


@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Account:
    """
    Get account details by ID

    Args:
        account_id: Account ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Account details

    Raises:
        404: If account not found or doesn't belong to user
    """
    try:
        banking_service = get_banking_service(db)
        account = await banking_service.get_account(account_id)

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account {account_id} not found",
            )

        # Verify account belongs to current user
        if account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this account",
            )

        return account

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch account",
        )


@router.get("/accounts/{account_id}/summary", response_model=AccountSummaryResponse)
async def get_account_summary(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get comprehensive account summary with statistics

    Args:
        account_id: Account ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Account summary with balance, transactions, and statistics
    """
    try:
        banking_service = get_banking_service(db)

        # Verify account belongs to user
        account = await banking_service.get_account(account_id)
        if not account or account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this account",
            )

        summary = await banking_service.get_account_summary(account_id)
        return summary

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch account summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch account summary",
        )


@router.get("/balance/{account_id}", response_model=BalanceResponse)
async def get_balance(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> BalanceResponse:
    """
    Get current balance for an account

    Args:
        account_id: Account ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Current account balance
    """
    try:
        banking_service = get_banking_service(db)

        # Get account and verify ownership
        account = await banking_service.get_account(account_id)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Account {account_id} not found",
            )

        if account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this account",
            )

        balance = await banking_service.get_balance(account_id)

        return BalanceResponse(
            account_id=account.id,
            account_number=account.account_number,
            balance=balance,
            currency=account.currency,
            as_of=datetime.utcnow(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch balance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch balance",
        )


@router.post("/deposit", response_model=TransactionResponse)
async def deposit(
    request: DepositRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Transaction:
    """
    Deposit funds into an account

    Args:
        request: Deposit request
        current_user: Authenticated user
        db: Database session

    Returns:
        Transaction record
    """
    try:
        banking_service = get_banking_service(db)

        # Verify account ownership
        account = await banking_service.get_account(request.account_id)
        if not account or account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this account",
            )

        logger.info(
            f"User {current_user.id} depositing {request.amount} to account {request.account_id}"
        )

        transaction = await banking_service.deposit(
            account_id=request.account_id,
            amount=request.amount,
            description=request.description,
            reference=request.reference,
        )

        return transaction

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Deposit failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deposit failed: {str(e)}",
        )


@router.post("/withdraw", response_model=TransactionResponse)
async def withdraw(
    request: WithdrawRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Transaction:
    """
    Withdraw funds from an account

    Args:
        request: Withdrawal request
        current_user: Authenticated user
        db: Database session

    Returns:
        Transaction record

    Raises:
        400: If insufficient funds
    """
    try:
        banking_service = get_banking_service(db)

        # Verify account ownership
        account = await banking_service.get_account(request.account_id)
        if not account or account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this account",
            )

        logger.info(
            f"User {current_user.id} withdrawing {request.amount} from account {request.account_id}"
        )

        transaction = await banking_service.withdraw(
            account_id=request.account_id,
            amount=request.amount,
            description=request.description,
            reference=request.reference,
        )

        return transaction

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Withdrawal failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Withdrawal failed: {str(e)}",
        )


@router.post("/transfer", response_model=TransferResponse)
async def transfer(
    request: TransferRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> TransferResponse:
    """
    Transfer funds between accounts

    Args:
        request: Transfer request
        current_user: Authenticated user
        db: Database session

    Returns:
        Transfer response with both transactions

    Raises:
        400: If insufficient funds or invalid accounts
        403: If user doesn't own source account
    """
    try:
        banking_service = get_banking_service(db)

        # Verify source account ownership
        from_account = await banking_service.get_account(request.from_account_id)
        if not from_account or from_account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to source account",
            )

        logger.info(
            f"User {current_user.id} transferring {request.amount} from "
            f"account {request.from_account_id} to {request.to_account_id}"
        )

        result = await banking_service.transfer(
            from_account_id=request.from_account_id,
            to_account_id=request.to_account_id,
            amount=request.amount,
            description=request.description,
            reference=request.reference,
        )

        # Get updated balances
        from_account_updated = await banking_service.get_account(
            request.from_account_id
        )
        to_account_updated = await banking_service.get_account(request.to_account_id)

        return TransferResponse(
            debit_transaction=result["debit"],
            credit_transaction=result["credit"],
            from_account_balance=from_account_updated.balance,
            to_account_balance=to_account_updated.balance,
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Transfer failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transfer failed: {str(e)}",
        )


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    account_id: int = Query(..., description="Account ID"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    transaction_type: Optional[TransactionType] = Query(
        None, description="Filter by transaction type"
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[Transaction]:
    """
    Get transaction history for an account

    Args:
        account_id: Account ID
        limit: Maximum number of transactions to return
        offset: Offset for pagination
        transaction_type: Optional filter by transaction type
        current_user: Authenticated user
        db: Database session

    Returns:
        List of transactions
    """
    try:
        banking_service = get_banking_service(db)

        # Verify account ownership
        account = await banking_service.get_account(account_id)
        if not account or account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this account",
            )

        transactions = await banking_service.get_transaction_history(
            account_id=account_id,
            limit=limit,
            offset=offset,
            transaction_type=transaction_type,
        )

        return transactions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch transactions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch transactions",
        )


@router.delete("/accounts/{account_id}")
async def close_account(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """
    Close/deactivate an account

    Args:
        account_id: Account ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        400: If account has non-zero balance
        403: If user doesn't own the account
    """
    try:
        banking_service = get_banking_service(db)

        # Verify account ownership
        account = await banking_service.get_account(account_id)
        if not account or account.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this account",
            )

        logger.info(f"User {current_user.id} closing account {account_id}")

        await banking_service.close_account(account_id)

        return {"message": f"Account {account.account_number} closed successfully"}

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to close account: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to close account",
        )
