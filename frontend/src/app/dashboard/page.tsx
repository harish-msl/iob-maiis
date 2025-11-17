'use client';

import { useEffect } from 'react';
import { useBankingStore } from '@/store/banking-store';
import { useAuthStore } from '@/store/auth-store';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Wallet,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight,
  Plus,
  CreditCard,
  DollarSign,
  Activity,
  Loader2
} from 'lucide-react';
import { formatCurrency, formatDate, formatRelativeTime, getTransactionColor, cn } from '@/lib/utils';
import Link from 'next/link';

export default function DashboardPage() {
  const { user } = useAuthStore();
  const { accounts, summary, fetchAccounts, fetchSummary, isLoading } = useBankingStore();

  useEffect(() => {
    fetchAccounts();
    fetchSummary();
  }, [fetchAccounts, fetchSummary]);

  if (isLoading && accounts.length === 0) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">Loading your accounts...</p>
        </div>
      </div>
    );
  }

  const totalBalance = summary?.total_balance || 0;
  const recentTransactions = summary?.recent_transactions || [];

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          Welcome back, {user?.full_name?.split(' ')[0] || 'User'}!
        </h1>
        <p className="text-muted-foreground mt-2">
          Here's what's happening with your accounts today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* Total Balance */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Balance</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(totalBalance)}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Across {accounts.length} {accounts.length === 1 ? 'account' : 'accounts'}
            </p>
          </CardContent>
        </Card>

        {/* Total Deposits */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Deposits</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {formatCurrency(summary?.statistics?.total_deposits || 0)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              All time deposits
            </p>
          </CardContent>
        </Card>

        {/* Total Withdrawals */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Withdrawals</CardTitle>
            <TrendingDown className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {formatCurrency(summary?.statistics?.total_withdrawals || 0)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              All time withdrawals
            </p>
          </CardContent>
        </Card>

        {/* Total Transfers */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Transfers</CardTitle>
            <Activity className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {formatCurrency(summary?.statistics?.total_transfers || 0)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              All time transfers
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Accounts Overview */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold tracking-tight">Your Accounts</h2>
            <p className="text-sm text-muted-foreground">Manage your banking accounts</p>
          </div>
          <Link href="/dashboard/accounts">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Account
            </Button>
          </Link>
        </div>

        {accounts.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Wallet className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No accounts yet</h3>
              <p className="text-sm text-muted-foreground mb-4 text-center max-w-sm">
                Get started by creating your first bank account. It only takes a few seconds.
              </p>
              <Link href="/dashboard/accounts">
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Create Your First Account
                </Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {accounts.map((account) => (
              <Card key={account.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                        <CreditCard className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <CardTitle className="text-base capitalize">
                          {account.account_type}
                        </CardTitle>
                        <CardDescription className="text-xs">
                          {account.account_number}
                        </CardDescription>
                      </div>
                    </div>
                    <Badge variant={account.is_active ? 'success' : 'destructive'}>
                      {account.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div>
                      <p className="text-sm text-muted-foreground">Balance</p>
                      <p className="text-2xl font-bold">
                        {formatCurrency(account.balance, account.currency)}
                      </p>
                    </div>
                    <div className="flex gap-2 pt-2">
                      <Link href={`/dashboard/accounts/${account.id}`} className="flex-1">
                        <Button variant="outline" size="sm" className="w-full">
                          View Details
                        </Button>
                      </Link>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Recent Transactions */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold tracking-tight">Recent Transactions</h2>
            <p className="text-sm text-muted-foreground">Your latest account activity</p>
          </div>
          <Link href="/dashboard/accounts">
            <Button variant="outline">View All</Button>
          </Link>
        </div>

        <Card>
          {recentTransactions.length === 0 ? (
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Activity className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No transactions yet</h3>
              <p className="text-sm text-muted-foreground text-center max-w-sm">
                Your transaction history will appear here once you start using your accounts.
              </p>
            </CardContent>
          ) : (
            <CardContent className="p-0">
              <div className="divide-y">
                {recentTransactions.slice(0, 10).map((transaction) => (
                  <div
                    key={transaction.id}
                    className="flex items-center justify-between p-4 hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div className={cn(
                        'flex h-10 w-10 items-center justify-center rounded-full',
                        transaction.transaction_type === 'deposit' && 'bg-green-100 dark:bg-green-900/20',
                        transaction.transaction_type === 'withdrawal' && 'bg-red-100 dark:bg-red-900/20',
                        transaction.transaction_type === 'transfer' && 'bg-blue-100 dark:bg-blue-900/20'
                      )}>
                        {transaction.transaction_type === 'deposit' && (
                          <ArrowDownRight className="h-5 w-5 text-green-600" />
                        )}
                        {transaction.transaction_type === 'withdrawal' && (
                          <ArrowUpRight className="h-5 w-5 text-red-600" />
                        )}
                        {transaction.transaction_type === 'transfer' && (
                          <ArrowUpRight className="h-5 w-5 text-blue-600" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium capitalize">
                          {transaction.transaction_type}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {transaction.description || 'No description'}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {formatRelativeTime(new Date(transaction.created_at))}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={cn(
                        'font-semibold',
                        getTransactionColor(transaction.transaction_type)
                      )}>
                        {transaction.transaction_type === 'withdrawal' ? '-' : '+'}
                        {formatCurrency(transaction.amount)}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Balance: {formatCurrency(transaction.balance_after)}
                      </p>
                      <Badge
                        variant={
                          transaction.status === 'completed' ? 'success' :
                          transaction.status === 'pending' ? 'warning' :
                          'destructive'
                        }
                        className="mt-1"
                      >
                        {transaction.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          )}
        </Card>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight mb-4">Quick Actions</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Link href="/dashboard/chat">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-900/20">
                    <Activity className="h-4 w-4 text-blue-600" />
                  </div>
                  AI Assistant
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Chat with AI to manage your accounts and get insights
                </p>
              </CardContent>
            </Card>
          </Link>

          <Link href="/dashboard/accounts">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-green-100 dark:bg-green-900/20">
                    <Wallet className="h-4 w-4 text-green-600" />
                  </div>
                  Manage Accounts
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  View, create, and manage your banking accounts
                </p>
              </CardContent>
            </Card>
          </Link>

          <Link href="/dashboard/documents">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-purple-100 dark:bg-purple-900/20">
                    <Activity className="h-4 w-4 text-purple-600" />
                  </div>
                  Documents
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Upload and process your banking documents
                </p>
              </CardContent>
            </Card>
          </Link>

          <Link href="/dashboard/voice">
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-orange-100 dark:bg-orange-900/20">
                    <Activity className="h-4 w-4 text-orange-600" />
                  </div>
                  Voice Banking
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Use voice commands to interact with your accounts
                </p>
              </CardContent>
            </Card>
          </Link>
        </div>
      </div>
    </div>
  );
}
