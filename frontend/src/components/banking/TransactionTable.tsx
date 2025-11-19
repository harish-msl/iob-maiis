"use client";

import React, { useState, useMemo } from "react";
import {
  ArrowUpRight,
  ArrowDownLeft,
  Search,
  Download,
  Calendar,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils/cn";
import { formatCurrency, formatDate } from "@/lib/utils/format";
import type { Transaction } from "@/lib/types/banking";

interface TransactionTableProps {
  transactions: Transaction[];
  accountId?: string;
  loading?: boolean;
  className?: string;
}

type TransactionType = "all" | "deposit" | "withdrawal" | "transfer";
type SortField = "date" | "amount" | "description";
type SortOrder = "asc" | "desc";

export function TransactionTable({
  transactions,
  loading = false,
  className,
}: TransactionTableProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState<TransactionType>("all");
  const [sortField, setSortField] = useState<SortField>("date");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Filter and sort transactions
  const filteredTransactions = useMemo(() => {
    let filtered = [...transactions];

    // Apply type filter
    if (typeFilter !== "all") {
      filtered = filtered.filter((tx) => tx.type.toLowerCase() === typeFilter);
    }

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (tx) =>
          tx.description?.toLowerCase().includes(query) ||
          tx.id?.toLowerCase().includes(query) ||
          tx.reference_number?.toLowerCase().includes(query),
      );
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let comparison = 0;

      switch (sortField) {
        case "date":
          comparison =
            new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
          break;
        case "amount":
          comparison = a.amount - b.amount;
          break;
        case "description":
          comparison = (a.description || "").localeCompare(b.description || "");
          break;
      }

      return sortOrder === "asc" ? comparison : -comparison;
    });

    return filtered;
  }, [transactions, typeFilter, searchQuery, sortField, sortOrder]);

  // Pagination
  const totalPages = Math.ceil(filteredTransactions.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedTransactions = filteredTransactions.slice(
    startIndex,
    endIndex,
  );

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortOrder("desc");
    }
  };

  const getTransactionIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case "deposit":
      case "credit":
        return <ArrowDownLeft className="h-4 w-4 text-green-500" />;
      case "withdrawal":
      case "debit":
        return <ArrowUpRight className="h-4 w-4 text-red-500" />;
      case "transfer":
        return <ArrowUpRight className="h-4 w-4 text-blue-500" />;
      default:
        return <ArrowUpRight className="h-4 w-4 text-gray-500" />;
    }
  };

  const getTransactionColor = (type: string) => {
    switch (type.toLowerCase()) {
      case "deposit":
      case "credit":
        return "text-green-600 dark:text-green-400";
      case "withdrawal":
      case "debit":
        return "text-red-600 dark:text-red-400";
      case "transfer":
        return "text-blue-600 dark:text-blue-400";
      default:
        return "text-foreground";
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
        return <Badge variant="default">Completed</Badge>;
      case "pending":
        return <Badge variant="secondary">Pending</Badge>;
      case "failed":
        return (
          <Badge variant="outline" className="border-red-500 text-red-500">
            Failed
          </Badge>
        );
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const exportToCSV = () => {
    const headers = [
      "Date",
      "Description",
      "Type",
      "Amount",
      "Status",
      "Reference",
    ];
    const rows = filteredTransactions.map((tx) => [
      formatDate(tx.created_at),
      tx.description || "",
      tx.type,
      tx.amount.toString(),
      tx.status,
      tx.reference_number || "",
    ]);

    const csv = [headers, ...rows].map((row) => row.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `transactions-${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
  };

  if (loading) {
    return (
      <Card className={cn("p-6", className)}>
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex items-center gap-4">
              <div className="h-10 w-10 animate-pulse rounded-lg bg-muted" />
              <div className="flex-1 space-y-2">
                <div className="h-4 w-1/3 animate-pulse rounded bg-muted" />
                <div className="h-3 w-1/4 animate-pulse rounded bg-muted" />
              </div>
              <div className="h-4 w-20 animate-pulse rounded bg-muted" />
            </div>
          ))}
        </div>
      </Card>
    );
  }

  if (transactions.length === 0) {
    return (
      <Card className={cn("p-12 text-center", className)}>
        <div className="mx-auto max-w-md">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-muted">
            <Calendar className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="mb-2 text-lg font-semibold">No Transactions Yet</h3>
          <p className="text-sm text-muted-foreground">
            Transactions will appear here once you start using your account.
          </p>
        </div>
      </Card>
    );
  }

  return (
    <div className={cn("space-y-4", className)}>
      {/* Filters and Search */}
      <Card className="p-4">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          {/* Search */}
          <div className="relative flex-1 lg:max-w-sm">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search transactions..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>

          {/* Filters */}
          <div className="flex flex-wrap items-center gap-2">
            {/* Type Filter */}
            <div className="flex items-center gap-1 rounded-lg border p-1">
              {(
                [
                  "all",
                  "deposit",
                  "withdrawal",
                  "transfer",
                ] as TransactionType[]
              ).map((type) => (
                <button
                  key={type}
                  onClick={() => {
                    setTypeFilter(type);
                    setCurrentPage(1);
                  }}
                  className={cn(
                    "rounded px-3 py-1.5 text-sm font-medium transition-colors",
                    typeFilter === type
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-muted",
                  )}
                >
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
            </div>

            {/* Export Button */}
            <Button
              variant="outline"
              size="sm"
              onClick={exportToCSV}
              disabled={filteredTransactions.length === 0}
            >
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
          </div>
        </div>

        {/* Results count */}
        <div className="mt-4 text-sm text-muted-foreground">
          Showing {startIndex + 1}-
          {Math.min(endIndex, filteredTransactions.length)} of{" "}
          {filteredTransactions.length} transaction
          {filteredTransactions.length !== 1 ? "s" : ""}
        </div>
      </Card>

      {/* Transactions Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="p-4 text-left">
                  <button
                    onClick={() => handleSort("date")}
                    className="flex items-center gap-1 font-semibold hover:text-primary"
                  >
                    Date
                    {sortField === "date" && (
                      <span className="text-xs">
                        {sortOrder === "asc" ? "↑" : "↓"}
                      </span>
                    )}
                  </button>
                </th>
                <th className="p-4 text-left">
                  <button
                    onClick={() => handleSort("description")}
                    className="flex items-center gap-1 font-semibold hover:text-primary"
                  >
                    Description
                    {sortField === "description" && (
                      <span className="text-xs">
                        {sortOrder === "asc" ? "↑" : "↓"}
                      </span>
                    )}
                  </button>
                </th>
                <th className="p-4 text-left font-semibold">Type</th>
                <th className="p-4 text-right">
                  <button
                    onClick={() => handleSort("amount")}
                    className="flex items-center gap-1 font-semibold hover:text-primary ml-auto"
                  >
                    Amount
                    {sortField === "amount" && (
                      <span className="text-xs">
                        {sortOrder === "asc" ? "↑" : "↓"}
                      </span>
                    )}
                  </button>
                </th>
                <th className="p-4 text-center font-semibold">Status</th>
              </tr>
            </thead>
            <tbody>
              {paginatedTransactions.map((transaction, index) => (
                <tr
                  key={transaction.id || index}
                  className="border-b transition-colors hover:bg-muted/50"
                >
                  <td className="p-4">
                    <div className="flex flex-col">
                      <span className="font-medium">
                        {formatDate(transaction.created_at, {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        })}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {new Date(transaction.created_at).toLocaleTimeString(
                          [],
                          {
                            hour: "2-digit",
                            minute: "2-digit",
                          },
                        )}
                      </span>
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
                        {getTransactionIcon(transaction.type)}
                      </div>
                      <div className="flex flex-col">
                        <span className="font-medium">
                          {transaction.description || "No description"}
                        </span>
                        {transaction.reference_number && (
                          <span className="text-xs text-muted-foreground">
                            Ref: {transaction.reference_number}
                          </span>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="p-4">
                    <Badge variant="outline">{transaction.type}</Badge>
                  </td>
                  <td className="p-4 text-right">
                    <span
                      className={cn(
                        "text-lg font-semibold",
                        getTransactionColor(transaction.type),
                      )}
                    >
                      {transaction.type.toLowerCase() === "debit" ? "-" : "+"}
                      {formatCurrency(Math.abs(transaction.amount))}
                    </span>
                  </td>
                  <td className="p-4 text-center">
                    {getStatusBadge(transaction.status)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between border-t p-4">
            <div className="text-sm text-muted-foreground">
              Page {currentPage} of {totalPages}
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() =>
                  setCurrentPage((p) => Math.min(totalPages, p + 1))
                }
                disabled={currentPage === totalPages}
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
