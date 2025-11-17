'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Plus, RefreshCw, TrendingUp, Wallet } from 'lucide-react';
import { AccountCard } from '@/components/banking/AccountCard';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { useBankingStore } from '@/store/banking-store';
import { cn } from '@/lib/utils/cn';
import { formatCurrency } from '@/lib/utils/format';

export default function AccountsPage() {
  const router = useRouter();
  const {
    accounts,
    summary,
    isLoading,
    error,
    fetchAccounts,
    fetchSummary,
  } = useBankingStore();

  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      await Promise.all([fetchAccounts(), fetchSummary()]);
    };
    loadData();
  }, [fetchAccounts, fetchSummary]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await Promise.all([fetchAccounts(), fetchSummary()]);
    setIsRefreshing(false);
  };

  const handleAccountClick = (accountId: string) => {
    router.push(`/dashboard/accounts/${accountId}`);
  };

  const activeAccounts = accounts.filter((acc) => acc.status === 'active');
  const inactiveAccounts = accounts.filter((acc) => acc.status !== 'active');

  const totalBalance = accounts.reduce((sum, acc) => sum + acc.balance, 0);
  const checkingBalance = accounts
    .filter((acc) => acc.account_type === 'checking')
    .reduce((sum, acc) => sum + acc.balance, 0);
  const savingsBalance = accounts
    .filter((acc) => acc.account_type === 'savings')
    .reduce((sum, acc) => sum + acc.balance, 0);

  if (isLoading && accounts.length === 0) {
    return (
      <div className="container mx-auto space-y-6 p-6">
        {/* Loading skeleton */}
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="h-8 w-48 animate-pulse rounded bg-muted" />
            <div className="h-4 w-64 animate-pulse rounded bg-muted" />
          </div>
          <div className="h-10 w-32 animate-pulse rounded bg-muted" />
        </div>

        {/* Summary cards skeleton */}
        <div className="grid gap-4 md:grid-cols-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-32 animate-pulse rounded-lg bg-muted" />
          ))}
        </div>

        {/* Account cards skeleton */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-64 animate-pulse rounded-lg bg-muted" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Accounts</h1>
          <p className="text-muted-foreground">
            Manage your bank accounts and view balances
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            <RefreshCw
              className={cn('mr-2 h-4 w-4', isRefreshing && 'animate-spin')}
            />
            Refresh
          </Button>
          <Button onClick={() => router.push('/dashboard/accounts/new')}>
            <Plus className="mr-2 h-4 w-4" />
            New Account
          </Button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <Card className="border-destructive/50 bg-destructive/10 p-4">
          <p className="text-sm text-destructive">{error}</p>
        </Card>
      )}

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        {/* Total Balance */}
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Total Balance
              </p>
              <p className="mt-2 text-3xl font-bold">
                {formatCurrency(summary?.total_balance || totalBalance)}
              </p>
            </div>
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
              <Wallet className="h-6 w-6 text-primary" />
            </div>
          </div>
          <p className="mt-4 text-xs text-muted-foreground">
            Across {activeAccounts.length} active account
            {activeAccounts.length !== 1 ? 's' : ''}
          </p>
        </Card>

        {/* Checking Total */}
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Checking Accounts
              </p>
              <p className="mt-2 text-3xl font-bold">
                {formatCurrency(checkingBalance)}
              </p>
            </div>
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-500/10">
              <TrendingUp className="h-6 w-6 text-blue-500" />
            </div>
          </div>
          <p className="mt-4 text-xs text-muted-foreground">
            {accounts.filter((a) => a.account_type === 'checking').length}{' '}
            checking account(s)
          </p>
        </Card>

        {/* Savings Total */}
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Savings Accounts
              </p>
              <p className="mt-2 text-3xl font-bold">
                {formatCurrency(savingsBalance)}
              </p>
            </div>
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-500/10">
              <TrendingUp className="h-6 w-6 text-green-500" />
            </div>
          </div>
          <p className="mt-4 text-xs text-muted-foreground">
            {accounts.filter((a) => a.account_type === 'savings').length} savings
            account(s)
          </p>
        </Card>
      </div>

      {/* Active Accounts */}
      {activeAccounts.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Active Accounts</h2>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {activeAccounts.map((account) => (
              <AccountCard
                key={account.id}
                account={account}
                onSelect={() => handleAccountClick(account.id)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Inactive Accounts */}
      {inactiveAccounts.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-muted-foreground">
            Inactive Accounts
          </h2>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {inactiveAccounts.map((account) => (
              <AccountCard
                key={account.id}
                account={account}
                onSelect={() => handleAccountClick(account.id)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {accounts.length === 0 && !isLoading && (
        <Card className="p-12 text-center">
          <div className="mx-auto max-w-md">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted">
              <Wallet className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="mb-2 text-lg font-semibold">No Accounts Yet</h3>
            <p className="mb-6 text-sm text-muted-foreground">
              Get started by creating your first bank account. You can create
              checking, savings, or investment accounts.
            </p>
            <Button onClick={() => router.push('/dashboard/accounts/new')}>
              <Plus className="mr-2 h-4 w-4" />
              Create Account
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}
