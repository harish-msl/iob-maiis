'use client';

import React, { useMemo } from 'react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils/cn';
import { formatCurrency } from '@/lib/utils/format';
import type { Transaction } from '@/lib/types/banking';

interface TransactionChartProps {
  transactions: Transaction[];
  type?: 'area' | 'bar' | 'pie';
  timeRange?: 'week' | 'month' | 'year';
  className?: string;
}

const COLORS = {
  deposit: '#10b981',
  withdrawal: '#ef4444',
  transfer: '#3b82f6',
  income: '#10b981',
  expense: '#ef4444',
};

const PIE_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export function TransactionChart({
  transactions,
  type = 'area',
  timeRange = 'month',
  className,
}: TransactionChartProps) {
  const chartData = useMemo(() => {
    if (transactions.length === 0) return [];

    // Sort transactions by date
    const sorted = [...transactions].sort(
      (a, b) =>
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    );

    // Get date range
    const now = new Date();
    let startDate: Date;

    switch (timeRange) {
      case 'week':
        startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case 'month':
        startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        break;
      case 'year':
        startDate = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
        break;
      default:
        startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
    }

    // Filter transactions within range
    const filtered = sorted.filter(
      (tx) => new Date(tx.created_at) >= startDate
    );

    if (type === 'pie') {
      // Group by transaction type for pie chart
      const grouped = filtered.reduce((acc, tx) => {
        const type = tx.type;
        if (!acc[type]) {
          acc[type] = 0;
        }
        acc[type] += Math.abs(tx.amount);
        return acc;
      }, {} as Record<string, number>);

      return Object.entries(grouped).map(([name, value]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        value,
      }));
    }

    // Group by date for area/bar charts
    const grouped = filtered.reduce((acc, tx) => {
      const date = new Date(tx.created_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      });

      if (!acc[date]) {
        acc[date] = { date, income: 0, expense: 0 };
      }

      if (tx.type === 'credit') {
        acc[date].income += tx.amount;
      } else {
        acc[date].expense += Math.abs(tx.amount);
      }

      return acc;
    }, {} as Record<string, { date: string; income: number; expense: number }>);

    return Object.values(grouped);
  }, [transactions, type, timeRange]);

  const totalIncome = useMemo(
    () =>
      transactions
        .filter(
          (tx) =>
            tx.type === 'credit'
        )
        .reduce((sum, tx) => sum + tx.amount, 0),
    [transactions]
  );

  const totalExpense = useMemo(
    () =>
      transactions
        .filter(
          (tx) =>
            tx.type === 'debit'
        )
        .reduce((sum, tx) => sum + Math.abs(tx.amount), 0),
    [transactions]
  );

  if (chartData.length === 0) {
    return (
      <Card className={cn('p-12 text-center', className)}>
        <div className="mx-auto max-w-md">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted">
            <svg
              className="h-8 w-8 text-muted-foreground"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
          </div>
          <h3 className="mb-2 text-lg font-semibold">No Data Available</h3>
          <p className="text-sm text-muted-foreground">
            Transaction data will appear here once you have activity in the selected
            time range.
          </p>
        </div>
      </Card>
    );
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    if (type === 'pie') {
      return (
        <div className="rounded-lg border bg-background p-3 shadow-lg">
          <p className="font-semibold">{payload[0].name}</p>
          <p className="text-sm text-muted-foreground">
            {formatCurrency(payload[0].value)}
          </p>
        </div>
      );
    }

    return (
      <div className="rounded-lg border bg-background p-3 shadow-lg">
        <p className="mb-2 font-semibold">{payload[0].payload.date}</p>
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center justify-between gap-4">
            <span className="text-sm capitalize" style={{ color: entry.color }}>
              {entry.name}:
            </span>
            <span className="font-semibold" style={{ color: entry.color }}>
              {formatCurrency(entry.value)}
            </span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <Card className={cn('p-6', className)}>
      {/* Header with stats */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">Transaction Overview</h3>
          <p className="text-sm text-muted-foreground">
            Last {timeRange === 'week' ? '7 days' : timeRange === 'month' ? '30 days' : 'year'}
          </p>
        </div>
        <div className="flex gap-4">
          <div className="text-right">
            <p className="text-xs text-muted-foreground">Income</p>
            <p className="text-lg font-bold text-green-600 dark:text-green-400">
              {formatCurrency(totalIncome)}
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs text-muted-foreground">Expenses</p>
            <p className="text-lg font-bold text-red-600 dark:text-red-400">
              {formatCurrency(totalExpense)}
            </p>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="h-[300px] w-full">
        {type === 'area' && (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorIncome" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.income} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={COLORS.income} stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorExpense" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.expense} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={COLORS.expense} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="date"
                className="text-xs"
                tick={{ fill: 'hsl(var(--muted-foreground))' }}
              />
              <YAxis
                className="text-xs"
                tick={{ fill: 'hsl(var(--muted-foreground))' }}
                tickFormatter={(value) => `$${value}`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Area
                type="monotone"
                dataKey="income"
                stroke={COLORS.income}
                fillOpacity={1}
                fill="url(#colorIncome)"
                name="Income"
              />
              <Area
                type="monotone"
                dataKey="expense"
                stroke={COLORS.expense}
                fillOpacity={1}
                fill="url(#colorExpense)"
                name="Expenses"
              />
            </AreaChart>
          </ResponsiveContainer>
        )}

        {type === 'bar' && (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="date"
                className="text-xs"
                tick={{ fill: 'hsl(var(--muted-foreground))' }}
              />
              <YAxis
                className="text-xs"
                tick={{ fill: 'hsl(var(--muted-foreground))' }}
                tickFormatter={(value) => `$${value}`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar dataKey="income" fill={COLORS.income} name="Income" radius={[4, 4, 0, 0]} />
              <Bar dataKey="expense" fill={COLORS.expense} name="Expenses" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}

        {type === 'pie' && (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) =>
                  `${name}: ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {chartData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Legend for pie chart */}
      {type === 'pie' && (
        <div className="mt-6 flex flex-wrap justify-center gap-4">
          {chartData.map((entry, index) => (
            <div key={index} className="flex items-center gap-2">
              <div
                className="h-3 w-3 rounded-sm"
                style={{ backgroundColor: PIE_COLORS[index % PIE_COLORS.length] }}
              />
              <span className="text-sm">
                {('name' in entry) ? entry.name : ''}:  {formatCurrency(('value' in entry) ? entry.value : 0)}
              </span>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
