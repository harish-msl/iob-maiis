import { create } from "zustand";
import { apiClient } from "@/lib/api/client";
import type {
  Account,
  Transaction,
  AccountSummary,
  Transfer,
} from "@/lib/types";

interface BankingState {
  accounts: Account[];
  selectedAccount: Account | null;
  transactions: Transaction[];
  summary: AccountSummary | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchAccounts: () => Promise<void>;
  fetchAccountById: (accountId: string) => Promise<void>;
  fetchTransactions: (accountId?: string) => Promise<void>;
  fetchAccountTransactions: (accountId: string) => Promise<void>;
  fetchSummary: () => Promise<void>;
  createTransfer: (data: Transfer) => Promise<void>;
  selectAccount: (account: Account | null) => void;
  clearError: () => void;
  reset: () => void;
}

export const useBankingStore = create<BankingState>((set, get) => ({
  accounts: [],
  selectedAccount: null,
  transactions: [],
  summary: null,
  isLoading: false,
  error: null,

  fetchAccounts: async () => {
    set({ isLoading: true, error: null });
    try {
      const accounts = await apiClient.getAccounts();
      set({ accounts, isLoading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch accounts",
        isLoading: false,
      });
      throw error;
    }
  },

  fetchAccountById: async (accountId: string) => {
    set({ isLoading: true, error: null });
    try {
      const account = await apiClient.getAccount(accountId);
      set({ selectedAccount: account, isLoading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch account",
        isLoading: false,
      });
      throw error;
    }
  },

  fetchTransactions: async (accountId?: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.getTransactions(accountId);
      const transactions = response.items || response;
      set({ transactions, isLoading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch transactions",
        isLoading: false,
      });
      throw error;
    }
  },

  fetchAccountTransactions: async (accountId: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await apiClient.getTransactions(accountId);
      const transactions = response.items || response;
      set({ transactions, isLoading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch account transactions",
        isLoading: false,
      });
      throw error;
    }
  },

  fetchSummary: async () => {
    set({ isLoading: true, error: null });
    try {
      const accounts = await apiClient.getAccounts();
      const totalBalance = accounts.reduce((sum, acc) => sum + acc.balance, 0);
      const activeAccounts = accounts.filter(
        (acc) => acc.status === "active",
      ).length;

      const response = await apiClient.getTransactions();
      const recentTransactions = (response.items || response).slice(0, 10);

      const summary: AccountSummary = {
        total_accounts: accounts.length,
        total_balance: totalBalance,
        active_accounts: activeAccounts,
        recent_transactions: recentTransactions,
      };

      set({ summary, isLoading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to fetch summary",
        isLoading: false,
      });
      throw error;
    }
  },

  createTransfer: async (data: Transfer) => {
    set({ isLoading: true, error: null });
    try {
      await apiClient.createTransfer(data);

      // Refresh accounts and transactions
      await get().fetchAccounts();
      await get().fetchTransactions();

      set({ isLoading: false });
    } catch (error: any) {
      set({
        error: error.message || "Failed to create transfer",
        isLoading: false,
      });
      throw error;
    }
  },

  selectAccount: (account: Account | null) => {
    set({ selectedAccount: account });
  },

  clearError: () => {
    set({ error: null });
  },

  reset: () => {
    set({
      accounts: [],
      selectedAccount: null,
      transactions: [],
      summary: null,
      isLoading: false,
      error: null,
    });
  },
}));
