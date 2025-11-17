'use client';

import React from 'react';
import { CreditCard, TrendingUp, TrendingDown, DollarSign, Eye, EyeOff } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils/cn';
import { formatCurrency, formatDate } from '@/lib/utils/format';
import type { Account } from '@/lib/types/banking';

interface AccountCardProps {
  account: Account;
  onSelect?: (account: Account) => void;
  showBalance?: boolean;
  className?: string;
}

export function AccountCard({
  account,
  onSelect,
  showBalance = true,
  className,
}: AccountCardProps) {
  const [balanceVisible, setBalanceVisible] = React.useState(showBalance);

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

  const getAccountTypeBadge = (type: string) => {
    switch (type.toLowerCase()) {
      case 'checking':
        return 'default';
      case 'savings':
        return 'secondary';
      case 'credit':
        return 'outline';
      default:
        return 'default';
    }
  };

  const getAccountIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'checking':
      case 'savings':
        return <CreditCard className="h-6 w-6" />;
      case 'credit':
        return <DollarSign className="h-6 w-6" />;
      default:
        return <CreditCard className="h-6 w-6" />;
    }
  };

  const isPositiveBalance = account.balance >= 0;
  const balanceChangePositive = (account.balance - (account.available_balance || account.balance)) >= 0;

  return (
    <Card
      className={cn(
        'group relative overflow-hidden transition-all hover:shadow-lg',
        onSelect && 'cursor-pointer hover:border-primary',
        className
      )}
      onClick={() => onSelect?.(account)}
    >
      {/* Colored accent bar */}
      <div className={cn('absolute left-0 top-0 h-full w-1.5', getAccountTypeColor(account.account_type))} />

      <div className="p-6 pl-8">
        {/* Header */}
        <div className="mb-4 flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div
              className={cn(
                'flex h-12 w-12 items-center justify-center rounded-lg text-white',
                getAccountTypeColor(account.account_type)
              )}
            >
              {getAccountIcon(account.account_type)}
            </div>
            <div>
              <h3 className="font-semibold text-foreground">{account.account_name}</h3>
              <p className="text-sm text-muted-foreground">
                •••• {account.account_number.slice(-4)}
              </p>
            </div>
          </div>
          <Badge variant={getAccountTypeBadge(account.account_type)}>
            {account.account_type}
          </Badge>
        </div>

        {/* Balance */}
        <div className="mb-4">
          <div className="mb-1 flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Current Balance</span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setBalanceVisible(!balanceVisible);
              }}
              className="rounded p-1 hover:bg-muted"
            >
              {balanceVisible ? (
                <EyeOff className="h-3 w-3 text-muted-foreground" />
              ) : (
                <Eye className="h-3 w-3 text-muted-foreground" />
              )}
            </button>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-bold">
              {balanceVisible ? (
                formatCurrency(account.balance)
              ) : (
                <span className="tracking-wider">••••••</span>
              )}
            </span>
            {account.currency !== 'USD' && (
              <span className="text-sm text-muted-foreground">{account.currency}</span>
            )}
          </div>
        </div>

        {/* Available Balance (if different) */}
        {account.available_balance !== undefined &&
          account.available_balance !== account.balance && (
            <div className="mb-4 flex items-center justify-between rounded-lg bg-muted/50 p-3">
              <span className="text-sm text-muted-foreground">Available</span>
              <span className="font-medium">
                {balanceVisible ? formatCurrency(account.available_balance) : '••••••'}
              </span>
            </div>
          )}

        {/* Stats */}
        <div className="flex items-center justify-between border-t pt-4">
          <div className="flex items-center gap-2 text-sm">
            <span className="text-muted-foreground">Status:</span>
            <Badge variant={account.status === 'active' ? 'default' : 'secondary'}>
              {account.status}
            </Badge>
          </div>

          {account.created_at && (
            <span className="text-xs text-muted-foreground">
              Opened {formatDate(account.created_at, 'short')}
            </span>
          )}
        </div>

        {/* Hover action */}
        {onSelect && (
          <div className="mt-4 opacity-0 transition-opacity group-hover:opacity-100">
            <Button variant="outline" size="sm" className="w-full">
              View Details
            </Button>
          </div>
        )}
      </div>
    </Card>
  );
}
