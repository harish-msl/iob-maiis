'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  Download,
  Upload,
  ArrowRightLeft,
  MoreVertical,
  Settings,
  Eye,
  EyeOff,
} from 'lucide-react';
import { TransactionTable } from '@/components/banking/TransactionTable';
import { TransferForm } from '@/components/banking/TransferForm';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/DropdownMenu';
import { useBankingStore } from '@/store/banking-store';
import { apiClient } from '@/lib/api/client';
import { cn } from '@/lib/utils/cn';
import { formatCurrency, formatDate } from '@/lib/utils/format';
import type { Transaction } from '@/lib/types/banking';

export default function AccountDetailPage() {
  const router = useRouter();
  const params = useParams();
  const accountId = params.id as string;

  const { accounts, fetchAccounts, fetchAccountTransactions } = useBankingStore();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showTransferForm, setShowTransferForm] = useState(false);
  const [balanceVisible, setBalanceVisible] = useState(true);

  const account = accounts.find((acc) => acc.id === accountId);

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // Fetch accounts if not already loaded
        if (accounts.length === 0) {
          await fetchAccounts();
        }

        // Fetch transactions
        const txData = await fetchAccountTransactions(accountId);
        setTransactions(txData);
      } catch (err: any) {
        setError(err.message || 'Failed to load account details');
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [accountId, fetchAccounts, fetchAccountTransactions, accounts.length]);

  const handleDeposit = async () => {
    // TODO: Implement deposit modal
    alert('Deposit functionality - to be implemented with dialog component');
  };

  const handleWithdraw = async () => {
    // TODO: Implement withdraw modal
    alert('Withdraw functionality - to be implemented with dialog component');
  };

  const handleTransfer = async (data: any) => {
    try {
      await apiClient.banking.transfer(data);
      // Refresh data
      await fetchAccounts();
      const txData = await fetchAccountTransactions(accountId);
      setTransactions(txData);
      setShowTransferForm(false);
    } catch (err: any) {
      throw new Error(err.response?.data?.detail || 'Transfer failed');
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto space-y-6 p-6">
        {/* Loading skeleton */}
        <div className="h-8 w-48 animate-pulse rounded bg-muted" />
        <div className="h-64 animate-pulse rounded-lg bg-muted" />
        <div className="h-96 animate-pulse rounded-lg bg-muted" />
      </div>
    );
  }

  if (error || !account) {
    return (
      <div className="container mx-auto p-6">
        <Card className="p-12 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10">
            <Settings className="h-8 w-8 text-destructive" />
          </div>
          <h3 className="mb-2 text-lg font-semibold">Account Not Found</h3>
          <p className="mb-6 text-sm text-muted-foreground">
            {error || 'The account you are looking for does not exist.'}
          </p>
          <Button onClick={() => router.push('/dashboard/accounts')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Accounts
          </Button>
        </Card>
      </div>
    );
  }

  const getAccountTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'checking':
        return 'bg-blue-500';
      case 'savings':
        return 'bg-green-500';
      case 'credit':
        return 'bg-purple-500';
      case 'investment':
        return 'bg-orange-500';
      default:
        return 'bg-gray-500';
    }
  };

  const recentTransactions = transactions.slice(0, 5);
  const totalIncome = transactions
    .filter((tx) => tx.transaction_type === 'deposit' || tx.transaction_type === 'credit')
    .reduce((sum, tx) => sum + tx.amount, 0);
  const totalExpenses = transactions
    .filter((tx) => tx.transaction_type === 'withdrawal' || tx.transaction_type === 'debit')
    .reduce((sum, tx) => sum + Math.abs(tx.amount), 0);

  return (
    <div className="container mx-auto space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <Button
          variant="ghost"
          onClick={() => router.push('/dashboard/accounts')}
          className="gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Accounts
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => setShowTransferForm(!showTransferForm)}>
              <ArrowRightLeft className="mr-2 h-4 w-4" />
              Transfer Money
            </DropdownMenuItem>
            <DropdownMenuItem onClick={handleDeposit}>
              <Download className="mr-2 h-4 w-4" />
              Deposit
            </DropdownMenuItem>
            <DropdownMenuItem onClick={handleWithdraw}>
              <Upload className="mr-2 h-4 w-4" />
              Withdraw
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Settings className="mr-2 h-4 w-4" />
              Account Settings
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Account Overview Card */}
      <Card className="relative overflow-hidden">
        <div
          className={cn('absolute left-0 top-0 h-full w-2', getAccountTypeColor(account.account_type))}
        />
        <div className="p-6 pl-8">
          <div className="mb-6 flex items-start justify-between">
            <div>
              <div className="mb-2 flex items-center gap-3">
                <h1 className="text-3xl font-bold">{account.account_name}</h1>
                <Badge>{account.account_type}</Badge>
                <Badge variant={account.status === 'active' ? 'default' : 'secondary'}>
                  {account.status}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                Account Number: •••• {account.account_number.slice(-4)}
              </p>
              {account.created_at && (
                <p className="text-xs text-muted-foreground">
                  Opened on {formatDate(account.created_at)}
                </p>
              )}
            </div>
            <button
              onClick={() => setBalanceVisible(!balanceVisible)}
              className="rounded p-2 hover:bg-muted"
            >
              {balanceVisible ? (
                <EyeOff className="h-5 w-5 text-muted-foreground" />
              ) : (
                <Eye className="h-5 w-5 text-muted-foreground" />
              )}
            </button>
          </div>

          {/* Balance Display */}
          <div className="mb-6">
            <p className="mb-2 text-sm text-muted-foreground">Current Balance</p>
            <div className="flex items-baseline gap-3">
              <h2 className="text-5xl font-bold">
                {balanceVisible ? (
                  formatCurrency(account.balance)
                ) : (
                  <span className="tracking-wider">••••••</span>
                )}
              </h2>
              {account.currency !== 'USD' && (
                <span className="text-xl text-muted-foreground">{account.currency}</span>
              )}
            </div>
            {account.available_balance !== undefined &&
              account.available_balance !== account.balance && (
                <p className="mt-2 text-sm text-muted-foreground">
                  Available: {balanceVisible ? formatCurrency(account.available_balance) : '••••••'}
                </p>
              )}
          </div>

          {/* Quick Stats */}
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-lg border bg-muted/50 p-4">
              <div className="flex items-center gap-2">
                <TrendingDown className="h-4 w-4 text-green-500" />
                <span className="text-sm text-muted-foreground">Total Income</span>
              </div>
              <p className="mt-2 text-2xl font-bold text-green-600 dark:text-green-400">
                {formatCurrency(totalIncome)}
              </p>
            </div>
            <div className="rounded-lg border bg-muted/50 p-4">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-red-500" />
                <span className="text-sm text-muted-foreground">Total Expenses</span>
              </div>
              <p className="mt-2 text-2xl font-bold text-red-600 dark:text-red-400">
                {formatCurrency(totalExpenses)}
              </p>
            </div>
            <div className="rounded-lg border bg-muted/50 p-4">
              <div className="flex items-center gap-2">
                <ArrowRightLeft className="h-4 w-4 text-blue-500" />
                <span className="text-sm text-muted-foreground">Transactions</span>
              </div>
              <p className="mt-2 text-2xl font-bold">{transactions.length}</p>
            </div>
          </div>
        </div>
      </Card>

      {/* Quick Actions */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Button
          onClick={handleDeposit}
          variant="outline"
          className="h-auto flex-col gap-2 p-6"
        >
          <Download className="h-6 w-6 text-green-500" />
          <div className="text-center">
            <p className="font-semibold">Deposit</p>
            <p className="text-xs text-muted-foreground">Add money to account</p>
          </div>
        </Button>
        <Button
          onClick={handleWithdraw}
          variant="outline"
          className="h-auto flex-col gap-2 p-6"
        >
          <Upload className="h-6 w-6 text-red-500" />
          <div className="text-center">
            <p className="font-semibold">Withdraw</p>
            <p className="text-xs text-muted-foreground">Take money out</p>
          </div>
        </Button>
        <Button
          onClick={() => setShowTransferForm(!showTransferForm)}
          variant="outline"
          className="h-auto flex-col gap-2 p-6"
        >
          <ArrowRightLeft className="h-6 w-6 text-blue-500" />
          <div className="text-center">
            <p className="font-semibold">Transfer</p>
            <p className="text-xs text-muted-foreground">Move between accounts</p>
          </div>
        </Button>
      </div>

      {/* Transfer Form */}
      {showTransferForm && (
        <TransferForm
          accounts={accounts}
          fromAccountId={accountId}
          onTransfer={handleTransfer}
          onCancel={() => setShowTransferForm(false)}
        />
      )}

      {/* Transactions */}
      <div>
        <h2 className="mb-4 text-2xl font-bold">Transaction History</h2>
        <TransactionTable
          transactions={transactions}
          accountId={accountId}
          loading={isLoading}
        />
      </div>
    </div>
  );
}
