// This file implements the consumption of a hypothetical REST API for the TradeEngine.
// All data models are defined in types.ts.
// The API endpoints and response structures are inferred from the Python TradeEngine class,
// as the API_DOCUMENTATION.md was not provided.

import { Candle, ActiveTrade, ClosedTrade, EquityHistoryEntry } from './types';

export class TradeEngineService {
    private baseUrl: string;

    /**
     * Initializes the TradeEngineService.
     * @param baseUrl The base URL for the TradeEngine API. Defaults to 'http://localhost:8000/api/trade-engine'.
     */
    constructor(baseUrl: string = 'http://localhost:8000/api/trade-engine') {
        this.baseUrl = baseUrl;
    }

    /**
     * Generic helper to fetch data from the API.
     * @param endpoint The API endpoint relative to the base URL.
     * @returns A Promise resolving to the fetched data of type T.
     * @throws An error if the network request fails or the response status is not OK.
     */
    private async fetchData<T>(endpoint: string): Promise<T> {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`);
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
            }
            return await response.json() as T;
        } catch (error) {
            console.error(`Error fetching data from ${endpoint}:`, error);
            throw error; // Re-throw to allow caller to handle
        }
    }

    /**
     * Fetches the current account balance.
     * Corresponds to Python's `TradeEngine.get_account_balance()`.
     * @returns Promise<number> The current account balance.
     */
    async getAccountBalance(): Promise<number> {
        return this.fetchData<number>('/balance');
    }

    /**
     * Fetches the current account equity (balance + unrealised P/L).
     * Corresponds to Python's `TradeEngine.get_account_equity()`.
     * @returns Promise<number> The current account equity.
     */
    async getAccountEquity(): Promise<number> {
        return this.fetchData<number>('/equity');
    }

    /**
     * Fetches the historical equity of the account.
     * Corresponds to Python's `TradeEngine.get_equity_history()`.
     * @returns Promise<EquityHistoryEntry[]> A list of historical equity entries.
     */
    async getEquityHistory(): Promise<EquityHistoryEntry[]> {
        return this.fetchData<EquityHistoryEntry[]>('/equity-history');
    }

    /**
     * Fetches all processed candle data.
     * Corresponds to Python's `TradeEngine.get_candle_data()`.
     * @returns Promise<Candle[]> A list of candle data.
     */
    async getCandleData(): Promise<Candle[]> {
        return this.fetchData<Candle[]>('/candles');
    }

    /**
     * Fetches a list of active trades.
     * Corresponds to Python's `TradeEngine.get_active_trades()`.
     * @param includePnl If true, requests the API to include the current unrealised P/L for each trade.
     * @param filters Optional key-value pairs to filter trades (e.g., { ticker: "EURUSD=X", type: "BUY" }).
     * @returns Promise<ActiveTrade[]> A list of active trades.
     */
    async getActiveTrades(includePnl: boolean = false, filters?: Record<string, any>): Promise<ActiveTrade[]> {
        let queryString = `?include_pnl=${includePnl}`;
        if (filters) {
            for (const key in filters) {
                if (Object.prototype.hasOwnProperty.call(filters, key)) {
                    queryString += `&${key}=${encodeURIComponent(filters[key])}`;
                }
            }
        }
        return this.fetchData<ActiveTrade[]>(`/trades/active${queryString}`);
    }

    /**
     * Fetches a list of closed trades.
     * Corresponds to Python's `TradeEngine.get_closed_trades()`.
     * @returns Promise<ClosedTrade[]> A list of closed trades.
     */
    async getClosedTrades(): Promise<ClosedTrade[]> {
        return this.fetchData<ClosedTrade[]>('/trades/closed');
    }

    /**
     * Fetches a list of historical trades.
     * In the Python implementation, this currently returns the same data as `get_closed_trades()`.
     * @returns Promise<ClosedTrade[]> A list of historical trades.
     */
    async getHistoricalTrades(): Promise<ClosedTrade[]> {
        return this.fetchData<ClosedTrade[]>('/trades/historical');
    }
}