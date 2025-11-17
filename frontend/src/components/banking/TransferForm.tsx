'use client';

import React, { useState } from 'react';
import { ArrowRight, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/Label';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { cn } from '@/lib/utils/cn';
import { formatCurrency } from '@/lib/utils/format';
import type { Account } from '@/lib/types/banking';

interface TransferFormProps {
  accounts: Account[];
  fromAccountId?: string;
  onTransfer: (data: TransferData) => Promise<void>;
  onCancel?: () => void;
  className?: string;
}

export interface TransferData {
  from_account_id: string;
  to_account_id: string;
  amount: number;
  description?: string;
}

export function TransferForm({
  accounts,
  fromAccountId,
  onTransfer,
  onCancel,
  className,
}: TransferFormProps) {
  const [fromAccount, setFromAccount] = useState(fromAccountId || '');
  const [toAccount, setToAccount] = useState('');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const selectedFromAccount = accounts.find((acc) => acc.id === fromAccount);
  const selectedToAccount = accounts.find((acc) => acc.id === toAccount);

  const availableFromAccounts = accounts.filter(
    (acc) => acc.status === 'active' && acc.account_type !== 'credit'
  );

  const availableToAccounts = accounts.filter(
    (acc) => acc.status === 'active' && acc.id !== fromAccount
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!fromAccount || !toAccount) {
      setError('Please select both accounts');
      return;
    }

    if (fromAccount === toAccount) {
      setError('Cannot transfer to the same account');
      return;
    }

    const transferAmount = parseFloat(amount);
    if (isNaN(transferAmount) || transferAmount <= 0) {
      setError('Please enter a valid amount');
      return;
    }

    if (selectedFromAccount && transferAmount > selectedFromAccount.balance) {
      setError('Insufficient funds');
      return;
    }

    setIsSubmitting(true);

    try {
      await onTransfer({
        from_account_id: fromAccount,
        to_account_id: toAccount,
        amount: transferAmount,
        description: description.trim() || undefined,
      });

      setSuccess(true);

      // Reset form after 2 seconds
      setTimeout(() => {
        setFromAccount(fromAccountId || '');
        setToAccount('');
        setAmount('');
        setDescription('');
        setSuccess(false);
      }, 2000);
    } catch (err: any) {
      setError(err.message || 'Transfer failed. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Allow only numbers and decimal point
    if (value === '' || /^\d*\.?\d*$/.test(value)) {
      setAmount(value);
    }
  };

  const setQuickAmount = (percentage: number) => {
    if (selectedFromAccount) {
      const quickAmount = (selectedFromAccount.balance * percentage).toFixed(2);
      setAmount(quickAmount);
    }
  };

  if (success) {
    return (
      <Card className={cn('p-8 text-center', className)}>
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-500/10">
          <CheckCircle2 className="h-8 w-8 text-green-500" />
        </div>
        <h3 className="mb-2 text-xl font-semibold">Transfer Successful!</h3>
        <p className="mb-4 text-sm text-muted-foreground">
          {formatCurrency(parseFloat(amount))} has been transferred successfully.
        </p>
      </Card>
    );
  }

  return (
    <Card className={cn('p-6', className)}>
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Header */}
        <div>
          <h2 className="text-2xl font-bold">Transfer Money</h2>
          <p className="text-sm text-muted-foreground">
            Move funds between your accounts
          </p>
        </div>

        {/* From Account */}
        <div className="space-y-2">
          <Label htmlFor="from-account">From Account</Label>
          <select
            id="from-account"
            value={fromAccount}
            onChange={(e) => setFromAccount(e.target.value)}
            disabled={isSubmitting || !!fromAccountId}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            required
          >
            <option value="">Select source account</option>
            {availableFromAccounts.map((account) => (
              <option key={account.id} value={account.id}>
                {account.account_name} - {formatCurrency(account.balance)}
              </option>
            ))}
          </select>
          {selectedFromAccount && (
            <div className="flex items-center justify-between rounded-lg border bg-muted/50 p-3">
              <div>
                <p className="text-sm font-medium">{selectedFromAccount.account_name}</p>
                <p className="text-xs text-muted-foreground">
                  •••• {selectedFromAccount.account_number.slice(-4)}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold">
                  {formatCurrency(selectedFromAccount.balance)}
                </p>
                <p className="text-xs text-muted-foreground">Available</p>
              </div>
            </div>
          )}
        </div>

        {/* Arrow Indicator */}
        <div className="flex justify-center">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
            <ArrowRight className="h-5 w-5 text-primary" />
          </div>
        </div>

        {/* To Account */}
        <div className="space-y-2">
          <Label htmlFor="to-account">To Account</Label>
          <select
            id="to-account"
            value={toAccount}
            onChange={(e) => setToAccount(e.target.value)}
            disabled={isSubmitting || !fromAccount}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            required
          >
            <option value="">Select destination account</option>
            {availableToAccounts.map((account) => (
              <option key={account.id} value={account.id}>
                {account.account_name} - {account.account_type}
              </option>
            ))}
          </select>
          {selectedToAccount && (
            <div className="flex items-center justify-between rounded-lg border bg-muted/50 p-3">
              <div>
                <p className="text-sm font-medium">{selectedToAccount.account_name}</p>
                <p className="text-xs text-muted-foreground">
                  •••• {selectedToAccount.account_number.slice(-4)}
                </p>
              </div>
              <Badge variant="secondary">{selectedToAccount.account_type}</Badge>
            </div>
          )}
        </div>

        {/* Amount */}
        <div className="space-y-2">
          <Label htmlFor="amount">Amount</Label>
          <div className="relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
              $
            </span>
            <Input
              id="amount"
              type="text"
              value={amount}
              onChange={handleAmountChange}
              placeholder="0.00"
              disabled={isSubmitting || !fromAccount}
              className="pl-7 text-lg font-semibold"
              required
            />
          </div>

          {/* Quick Amount Buttons */}
          {selectedFromAccount && selectedFromAccount.balance > 0 && (
            <div className="flex gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setQuickAmount(0.25)}
                disabled={isSubmitting}
              >
                25%
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setQuickAmount(0.5)}
                disabled={isSubmitting}
              >
                50%
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setQuickAmount(0.75)}
                disabled={isSubmitting}
              >
                75%
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setQuickAmount(1)}
                disabled={isSubmitting}
              >
                Max
              </Button>
            </div>
          )}
        </div>

        {/* Description */}
        <div className="space-y-2">
          <Label htmlFor="description">Description (Optional)</Label>
          <Input
            id="description"
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Enter transfer description"
            disabled={isSubmitting}
            maxLength={200}
          />
          <p className="text-xs text-muted-foreground">
            {description.length}/200 characters
          </p>
        </div>

        {/* Summary */}
        {fromAccount && toAccount && amount && parseFloat(amount) > 0 && (
          <div className="rounded-lg border bg-muted/50 p-4 space-y-2">
            <p className="text-sm font-semibold">Transfer Summary</p>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">From:</span>
                <span className="font-medium">{selectedFromAccount?.account_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">To:</span>
                <span className="font-medium">{selectedToAccount?.account_name}</span>
              </div>
              <div className="flex justify-between border-t pt-2">
                <span className="text-muted-foreground">Amount:</span>
                <span className="text-lg font-bold text-primary">
                  {formatCurrency(parseFloat(amount))}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="flex items-center gap-2 rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3">
          {onCancel && (
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              disabled={isSubmitting}
              className="flex-1"
            >
              Cancel
            </Button>
          )}
          <Button
            type="submit"
            disabled={isSubmitting || !fromAccount || !toAccount || !amount}
            className="flex-1"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                Transfer {amount && formatCurrency(parseFloat(amount))}
              </>
            )}
          </Button>
        </div>
      </form>
    </Card>
  );
}
