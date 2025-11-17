import { create } from 'zustand';
import { apiClient } from '@/lib/api-client';
import type {
  BankAccount,
  Transaction,
  AccountSummary,
  CreateAccountRequest,
  DepositRequest,
  WithdrawRequest,
  TransferRequest,
} from '@/types';

interface BankingState {
  accounts: BankAccount[];
  selectedAccount: BankAccount | null;
  transactions: Transaction[];
  summary: AccountSummary | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchAccounts: () => Promise<void>;
  fetchAccountById: (accountId: string) => Promise<void>;
  fetchTransactions: (accountId: string, limit?: number) => Promise<void>;
  fetchSummary: () => Promise<void>;
  createAccount: (data: CreateAccountRequest) => Promise<BankAccount>;
  deposit: (accountId: string, data: DepositRequest) => Promise<Transaction>;
  withdraw: (accountId: string, data: WithdrawRequest) => Promise<Transaction>;
  transfer: (data: TransferRequest) => Promise<{ transactions: Transaction[] }>;
  selectAccount: (account: BankAccount | null) => void;
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
        error: error.message || 'Failed to fetch accounts',
        isLoading: false,
      });
      throw error;
    }
  },

  fetchAccountById: async (accountId: string) => {
    set({ isLoading: true, error: null });
    try {
      const account = await apiClient.getAccountById(accountId);
      set({ selectedAccount: account, isLoading: false });
    } catch (error: any) {
      set({
        error: error.message || 'Failed to fetch account',
        isLoading: false,
      });
      throw error;
    }
  },

  fetchTransactions: async (accountId: string, limit: number = 50) => {
    set({ isLoading: true, error: null });
    try {
      const transactions = await apiClient.getTransactions(accountId, limit);
      set({ transactions, isLoading: false });
    } catch (error: any) {
      set({
        error: error.message || 'Failed to fetch transactions',
        isLoading: false,
      });
      throw error;
    }
  },

  fetchSummary: async () => {
    set({ isLoading: true, error: null });
    try {
      const summary = await apiClient.getAccountSummary();
      set({ summary, isLoading: false });
    } catch (error: any) {
      set({
        error: error.message || 'Failed to fetch summary',
        isLoading: false,
      });
      throw error;
    }
  },

  createAccount: async (data: CreateAccountRequest) => {
    set({ isLoading: true, error: null });
    try {
      const account = await apiClient.createAccount(data);
      set((state) => ({
        accounts: [...state.accounts, account],
        isLoading: false,
      }));
      return account;
    } catch (error: any) {
      set({
        error: error.message || 'Failed to create account',
        isLoading: false,
      });
      throw error;
    }
  },

  deposit: async (accountId: string, data: DepositRequest) => {
    set({ isLoading: true, error: null });
    try {
      const transaction = await apiClient.deposit(accountId, data.amount, data.description);

      // Update account balance
      set((state) => ({
        accounts: state.accounts.map((acc) =>
          acc.id === accountId ? { ...acc, balance: transaction.balance_after } : acc
        ),
        selectedAccount:
          state.selectedAccount?.id === accountId
            ? { ...state.selectedAccount, balance: transaction.balance_after }
            : state.selectedAccount,
        transactions: [transaction, ...state.transactions],
        isLoading: false,
      }));

      return transaction;
    } catch (error: any) {
      set({
        error: error.message || 'Failed to deposit',
        isLoading: false,
      });
      throw error;
    }
  },

  withdraw: async (accountId: string, data: WithdrawRequest) => {
    set({ isLoading: true, error: null });
    try {
      const transaction = await apiClient.withdraw(accountId, data.amount, data.description);

      // Update account balance
      set((state) => ({
        accounts: state.accounts.map((acc) =>
          acc.id === accountId ? { ...acc, balance: transaction.balance_after } : acc
        ),
        selectedAccount:
          state.selectedAccount?.id === accountId
            ? { ...state.selectedAccount, balance: transaction.balance_after }
            : state.selectedAccount,
        transactions: [transaction, ...state.transactions],
        isLoading: false,
      }));

      return transaction;
    } catch (error: any) {
      set({
        error: error.message || 'Failed to withdraw',
        isLoading: false,
      });
      throw error;
    }
  },

  transfer: async (data: TransferRequest) => {
    set({ isLoading: true, error: null });
    try {
      const result = await apiClient.transfer(
        data.from_account_id,
        data.to_account_id,
        data.amount,
        data.description
      );

      // Update both account balances
      const fromTransaction = result.transactions.find(
        (t) => t.account_id === data.from_account_id
      );
      const toTransaction = result.transactions.find((t) => t.account_id === data.to_account_id);

      set((state) => ({
        accounts: state.accounts.map((acc) => {
          if (acc.id === data.from_account_id && fromTransaction) {
            return { ...acc, balance: fromTransaction.balance_after };
          }
          if (acc.id === data.to_account_id && toTransaction) {
            return { ...acc, balance: toTransaction.balance_after };
          }
          return acc;
        }),
        transactions: [...result.transactions, ...state.transactions],
        isLoading: false,
      }));

      return result;
    } catch (error: any) {
      set({
        error: error.message || 'Failed to transfer',
        isLoading: false,
      });
      throw error;
    }
  },

  selectAccount: (account: BankAccount | null) => {
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
